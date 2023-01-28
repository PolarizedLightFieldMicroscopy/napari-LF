import sys, os
import numpy as np
from lflib.lightfield import LightField
from lflib.imageio import save_image
from scipy.ndimage import filters
os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
try:
    import pyopencl as cl
    import pyopencl.array as cl_array
    LFLIB_HAVE_OPENCL = True
except ImportError:
    LFLIB_HAVE_OPENCL = False
# Utility function
extract = lambda x, y: dict(list(zip(x, list(map(y.get, x)))))

# ------------------------------------------------------------------------------
#                               OPENCL KERNELS
# ------------------------------------------------------------------------------

src = '''

// Enable 64-bit double support
#if defined(cl_khr_fp64)  // Khronos extension available?
#pragma OPENCL EXTENSION cl_khr_fp64 : enable
#elif defined(cl_amd_fp64)  // AMD extension available?
#pragma OPENCL EXTENSION cl_amd_fp64 : enable
#endif

__kernel void cl_backproject_rayspread(__read_only image2d_t lf,
                                 __global float* volume,
                                 int lf_rows, int lf_cols,
                                 __global float* psf,
                                 __constant int* filterRows,
                                 __constant int* filterCols,
                                 __constant int* filterRowOffset,
                                 __constant int* filterColOffset,
                                 int supersample_factor,
                                 sampler_t sampler) {
  
  // Store each work-item unique row and column
  int x = get_global_id(0);        int y = get_global_id(1); 
  int s = x / supersample_factor;  int t = y / supersample_factor;

  // Bail out if the kernel is out of bounds
  if (x >= K_NX || y >= K_NY)
    return;

  // This offset comes into play when supersample_factor > 1
  int x_bump = (x - s * supersample_factor);
  int y_bump = (y - t * supersample_factor);
  
  // Iterator for the filter
  int base_address = 0;
  
  for (int z_idx = 0; z_idx < K_NZ; ++z_idx) {
    float sum = 0.0f;
    int2 coords;

    // Iterate the filter rows
    for(int j = y_bump; j < filterRows[z_idx]; j+=supersample_factor) {
      coords.y = (y - j - filterRowOffset[z_idx])/supersample_factor;

      // Iterate over the filter columns
      int filterIdx = base_address + filterCols[z_idx]*j + x_bump;
      for(int i = x_bump; i < filterCols[z_idx]; i+=supersample_factor) {
        coords.x = (x - i - filterColOffset[z_idx])/supersample_factor;

        // Read a pixel from the image. A single channel image
        // stores the pixel in the 'x' coordinate of the returned vector.
        float4 pixel = read_imagef(lf, sampler, coords);
        sum += pixel.x * psf[filterIdx];
        filterIdx += supersample_factor;
      }
    }

    // Copy the data to the output image if the work-item is in bounds
    int vol_idx = y*K_NX*K_NZ + x*K_NZ + z_idx;
    volume[vol_idx] += sum;
    base_address += (filterCols[z_idx] * filterRows[z_idx]);
  }
}

__kernel void cl_project_rayspread(__read_only image2d_t vol_slice,
                         __global float* subaperture,
                         __global float* psf,
                         __constant int* filterRows,
                         __constant int* filterCols,
                         __constant int* filterRowOffset,
                         __constant int* filterColOffset,
                         __constant int* u_coords,
                         __constant int* v_coords,
                         int num_rays,
                         int supersample_factor,
                         sampler_t sampler) {

  // Store each work-item unique row and column
  int s = get_global_id(0); int t = get_global_id(1);

  // Bail out if the kernel is out of bounds
  if (s >= K_NS || t >= K_NT)
    return;

  // Iterator for the filter
  int base_address = 0;

  for (int r = 0; r < num_rays; ++r) {
    float sum = 0.0f;
    int2 coords;

    // Iterate the filter rows
    for(int j = 0; j < filterRows[r]; ++j) {
      coords.y = t*supersample_factor + j + filterRowOffset[r];

      // Iterate over the filter columns
      int filterIdx = base_address + filterCols[r]*j;
      for(int i = 0; i < filterCols[r]; ++i) {
        coords.x = s*supersample_factor + i + filterColOffset[r];

        // Read a pixel from the image. A single channel image
        // stores the pixel in the 'x' coordinate of the returned vector.
        float4 pixel = read_imagef(vol_slice, sampler, coords);
        sum += pixel.x * psf[filterIdx++];
      }
    }

    // Copy the data to the output light field
    int u = u_coords[r];
    int v = v_coords[r];
    int subap_idx = v*K_NT*K_NU*K_NS + t*K_NU*K_NS + u*K_NS + s;
    subaperture[subap_idx] += sum;
    base_address += (filterCols[r] * filterRows[r]);
  }
  
}


__kernel void cl_project_wavespread(__read_only image2d_t vol_slice,
                             __global double* subaperture_im,
                             __global int* u_coords,
                             __global int* v_coords,
                             __global int* s_coords,
                             __global int* t_coords,
                             __global float* coefficients,
                             int num_coefficients,
                             int supersample_factor,
                             int dx, int dy,
                             sampler_t sampler) {

  // Create local storage to speed up running summations.
  __private double sum_buf[K_NU * K_NV];
//  __private float sum_total[K_NU * K_NV];
//  __private float num_good[K_NU * K_NV];
//  __private float num_total[K_NU * K_NV];
  for (int v = 0; v < K_NV; ++v) {
    for (int u = 0; u < K_NU; ++u) {
      sum_buf[v*K_NU+u] = 0.0;
//      sum_total[v*K_NU+u] = 0.0;
//      num_good[v*K_NU+u] = 0.0;
//      num_total[v*K_NU+u] = 0.0;
    }
  }
  
  // Store each work-item unique row and column
  int s = get_global_id(0); int t = get_global_id(1);

  // Bail out if the kernel is out of bounds
  if (s >= K_NS || t >= K_NT)
    return;

  // Iterate over the psf coordinates and coefficients
  for (int i = 0; i < num_coefficients; ++i) {

    // Grab the appropriate pixel from the volume.  Here we assume
    // that a value of s_coords = 0 and t_coords = 0 refer to the
    // lenslet at the center of the volume.
    //
    int2 coords;
    coords.x = (s - s_coords[i]) * supersample_factor + dx;
    coords.y = (t - t_coords[i]) * supersample_factor + dy;

    float4 pixel = read_imagef(vol_slice, sampler, coords);

    // Copy the data to the output light field
    int u = u_coords[i];
    int v = v_coords[i];
    //num_total[v*K_NU+u] += 1;
    //if (coords.x >= 0 && coords.x < K_NS && coords.y >= 0 && coords.y < K_NT) {
    //num_good[v*K_NU+u] += 1;
    //}
    
    sum_buf[v*K_NU+u] += pixel.x * coefficients[i];
  }

  for (int v = 0; v < K_NV; ++v) {
    for (int u = 0; u < K_NU; ++u) {
      int subap_idx = v*K_NT*K_NU*K_NS + t*K_NU*K_NS + u*K_NS + s;
      subaperture_im[subap_idx] += sum_buf[v*K_NU+u];
    }
  }
}

__kernel void cl_backproject_wavespread(__read_only image2d_t lf,
                                        __global double* volume,
                                        __global int* u_coords,
                                        __global int* v_coords,
                                        __global int* s_coords,
                                        __global int* t_coords,
                                        __global float* coefficients,
                                        int num_coefficients,
                                        int z, int dx, int dy,
                                        int supersample_factor,
                                        sampler_t sampler) {
  
  // Store each work-item unique row and column
  int s = get_global_id(0);
  int t = get_global_id(1);
  int x = s * supersample_factor + dx; 
  int y = t * supersample_factor + dy; 

  // Bail out if the kernel is out of bounds
  if (x >= K_NX || y >= K_NY || x < 0 || y < 0)
    return;

  double sum = 0.0;

  // Iterate over the psf coordinates and coefficients
  for (int i = 0; i < num_coefficients; ++i) {

    int2 coords;

    //float r = sqrt( (float) ((s - K_NS / 2) + (t - K_NT / 2)) );
    //float theta = atan2((float)(s - K_NS / 2), (float)(t - K_NT / 2));

    //float du = r * cos(theta);
    //float dv = r * sin(theta);

    // Check to make sure the s index is in bounds.
    int s_idx = s + s_coords[i];
    int t_idx = t + t_coords[i];
    if (s_idx < 0 || s_idx >= K_NS || t_idx < 0 || t_idx >= K_NT)
      continue;

    // Grab the appropriate pixel from the light field.  Here we assume
    // that a value of s_coords = 0 and t_coords = 0 refer to the
    // lenslet at the center of the volume.
    //
    coords.y = t_idx * K_NS + s_idx;
    coords.x = v_coords[i] * K_NU + u_coords[i];
    float4 pixel = read_imagef(lf, sampler, coords);

    // Copy the data to the output light field
    sum += pixel.x * coefficients[i];
  }
  int vol_idx = z*K_NX*K_NY + y*K_NX + x;
  volume[vol_idx] += sum;
}

'''

# ------------------------------------------------------------------------------
#                        UTILITY CLASSES & FUNCTIONS
# ------------------------------------------------------------------------------

def roundUp(value, multiple):
    ''' Determine how far past the nearest multiple of the value.
    This is useful for padding image dimensions to nice powers of 16,
    which helps promote efficient memory access on the GPU.'''
    
    remainder = value % multiple
    if remainder != 0:
        value += (multiple-remainder)
    return value

# ------------------------------------------------------------------------------
#                         LIGHT FIELD PROJECTION CLASS
# ------------------------------------------------------------------------------

class LightFieldProjection(object):

    def __init__(self, rayspread_db=None, psf_db=None, disable_gpu=False, gpu_id=None, platform_id=0, use_sing_prec=False):

        self.rayspread_db = rayspread_db
        self.psf_db = psf_db
        if self.psf_db is not None:
            db = self.psf_db
        else:
            db = self.rayspread_db

        # Premultiplier is optionally applied after forward
        # projection, and before back projection.
        #
        # Postmultiplier is optionally applied before forward
        # projection, and after back projection.
        #
        self.premultiplier = None
        self.postmultiplier = None
        
        if LFLIB_HAVE_OPENCL and not disable_gpu:
            # Set up OpenCL
            platform = cl.get_platforms()[platform_id]
            print(75*"=")
            print('platform id: ',platform_id, ' | platform: ',platform)
            try:
                for device in platform.get_devices():
                    print('device: ', device)
            except Exception as e:
                print("Error: ", e)
            print(75*"=")

            if sys.platform == "darwin":
                self.cl_ctx = cl.Context() 
            elif gpu_id is not None:
                self.cl_ctx = cl.Context(properties=[(cl.context_properties.PLATFORM, platform)],
                                         devices = [platform.get_devices()[gpu_id]])
            else:
                self.cl_ctx = cl.Context(properties=[(cl.context_properties.PLATFORM, platform)])

            # This poor-man's template substitution allows us to
            # hard-code some values in the kernel.
            preprocessed_src = src.replace('K_NU', str(db.nu))
            preprocessed_src = preprocessed_src.replace('K_NV', str(db.nv))
            preprocessed_src = preprocessed_src.replace('K_NS', str(db.ns))
            preprocessed_src = preprocessed_src.replace('K_NT', str(db.nt))
            preprocessed_src = preprocessed_src.replace('K_NX', str(db.nx))
            preprocessed_src = preprocessed_src.replace('K_NY', str(db.ny))
            preprocessed_src = preprocessed_src.replace('K_NZ', str(db.nz))
            
            if use_sing_prec:
                preprocessed_src = preprocessed_src.replace('double', 'float')
                print('Using single precision option (--use-single-precision)')

            self.cl_prog = cl.Program(self.cl_ctx, preprocessed_src).build()
            self.cl_queue = cl.CommandQueue(self.cl_ctx)

            # Set up OpenCL
            self.WORKGROUP_X = 16
            self.WORKGROUP_Y = 16
            self.WORKGROUP_Z = 1

            self.backproject = self.backproject_wavespread_gpu
            self.project = self.project_wavespread_gpu


        else:  # No OpenCL
            if self.psf_db is not None:
                raise Exception("WARNING: your platform does not seem to support OpenCL.  There is no project/backproject implementations for wavespreads on the CPU.   Exiting.")
            else:
                print("WARNING: your platform does not seem to support OpenCL.  Using SIRT CPU implementation.")
                self.backproject = self.backproject_cpu
                self.project = self.project_cpu

    def set_premultiplier(self, premultiplier):
        self.premultiplier = premultiplier

    def set_postmultiplier(self, postmultiplier):
        self.postmultiplier = postmultiplier

    # ============================================================================================
    #                              WAVESPREAD PROJECT/BACKPROJECT
    # ============================================================================================

    def project_wavespread_gpu( self, volume, use_sing_prec, zslice = None):
        """
        Using the given psf database, compute a light field by
        projecting the volume onto the light field sensor.
        
        Returns: A lightfield as a tiled set of sub-aperture
        (i.e. pinhole) images.
        """
        if self.postmultiplier is not None:
            vol = volume * self.postmultiplier
        else:
            vol = volume

        psf_coordinates = self.psf_db.psf_coordinates
        psf_coefficients = self.psf_db.psf_coefficients
        z_coords = self.psf_db.z_coords

        nu = self.psf_db.nu; nv = self.psf_db.nv;
        ns = self.psf_db.ns; nt = self.psf_db.nt;
        nx = self.psf_db.nx; ny = self.psf_db.ny; nz = self.psf_db.nz;
        supersample_factor = self.psf_db.supersample_factor

        # Create an empty lightfield image.
        if use_sing_prec:
            lf = np.zeros((nv * nt, nu * ns), dtype = np.float32)
            #print('Using single precision option')
        else:
            lf = np.zeros((nv * nt, nu * ns), dtype = np.float64)

        # Upload volume slices to the GPU
        vol_slices = {}
        samp = cl.Sampler(self.cl_ctx, False, cl.addressing_mode.CLAMP, cl.filter_mode.NEAREST)
        for z in range(vol.shape[2]):
            vol_slice = vol[:,:,z].astype(np.float32)
            vol_slices[z] = cl.image_from_array(self.cl_ctx, vol_slice.copy(), 1, 'r')
 
        # Create a set of empty subaperture images to accumulate data into
        if use_sing_prec:
            subaperture_buf = cl_array.zeros(self.cl_queue, (nt*nv, ns*nu), dtype=np.float32)
            #print('Using single precision option')
        else:
            subaperture_buf = cl_array.zeros(self.cl_queue, (nt*nv, ns*nu), dtype=np.float64)

        # Set static kernel arguments
        kern = self.cl_prog.cl_project_wavespread
        kern.set_arg(1, subaperture_buf.data)
        kern.set_arg(8, np.uint32(self.psf_db.supersample_factor))
        kern.set_arg(11, samp)

        # Workgroup and global sizes
        localSize = (self.WORKGROUP_X, self.WORKGROUP_Y)
        globalSize = (roundUp(ns, self.WORKGROUP_X),
                      roundUp(nt, self.WORKGROUP_Y))

        for z in range(nz):
            for x in range(supersample_factor):
                for y in range(supersample_factor):
                    coords = psf_coordinates[(x,y,z)]
                    coefficients = psf_coefficients[(x,y,z)]

                    # Extract the sorted coordinates. Copy here ensure
                    # "single segment" memory buffer, which seems to
                    # be required by cl.Buffer() below.
                    u_coords = coords[:,0].copy()
                    v_coords = coords[:,1].copy()
                    s_coords = coords[:,2].copy()
                    t_coords = coords[:,3].copy()

                    u_coords_buf = cl.Buffer(self.cl_ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
                                             hostbuf = u_coords)
                    v_coords_buf = cl.Buffer(self.cl_ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
                                             hostbuf = v_coords)
                    s_coords_buf = cl.Buffer(self.cl_ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
                                             hostbuf = s_coords)
                    t_coords_buf = cl.Buffer(self.cl_ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
                                             hostbuf = t_coords)
                    coefficients_buf = cl.Buffer(self.cl_ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
                                                 hostbuf=coefficients)

                    kern.set_arg(0, vol_slices[z])
                    kern.set_arg(2, u_coords_buf)
                    kern.set_arg(3, v_coords_buf)
                    kern.set_arg(4, s_coords_buf)
                    kern.set_arg(5, t_coords_buf)
                    kern.set_arg(6, coefficients_buf)
                    kern.set_arg(7, np.uint32(coefficients.shape[0])) # num_coefficients
                    kern.set_arg(9, np.uint32(x))
                    kern.set_arg(10, np.uint32(y))

                    # Execute the kernel
                    cl.enqueue_nd_range_kernel(self.cl_queue, kern, globalSize, localSize)

        # Download the result, and place the data for this
        # subaperture into the lightfield.
        self.cl_queue.finish()
        lf_im = subaperture_buf.get(self.cl_queue)
        lf = LightField(lf_im, self.psf_db.nu, self.psf_db.nv,
                        self.psf_db.ns, self.psf_db.nt,
                        representation = LightField.TILED_SUBAPERTURE)

        if self.premultiplier is not None:
            light_field_im = lf.asimage(LightField.TILED_LENSLET) * self.premultiplier
            lf = LightField(light_field_im, nu, nv, ns, nt,
                            representation = LightField.TILED_LENSLET)

        self.cl_queue.finish()
        return lf

    def backproject_wavespread_gpu(self, light_field, use_sing_prec):
        """
        Using the given psf database, compute focused images at the
        z_depths included in the supplied psf_db.
        
        Returns: A volume as a 3D numpy matrix that is indexed in [y,x,z]
        order.
        """
        psf_coordinates = self.psf_db.psf_coordinates
        psf_coefficients = self.psf_db.psf_coefficients
        
        z_coords = self.psf_db.z_coords

        nu = self.psf_db.nu
        nv = self.psf_db.nv
        ns = self.psf_db.ns
        nt = self.psf_db.nt
        nx = self.psf_db.nx
        ny = self.psf_db.ny
        nz = self.psf_db.nz
        supersample_factor = self.psf_db.supersample_factor

        # Optionally apply radiometry correction
        if self.premultiplier is not None:
            light_field_im = light_field.asimage(LightField.TILED_LENSLET) * self.premultiplier
            light_field = LightField(light_field_im, nu, nv, ns, nt,
                                     representation = LightField.TILED_LENSLET)

        # Create an empty volume
        if use_sing_prec:
            volume_buf = cl_array.zeros(self.cl_queue,
                                    (ny*nx*nz),
                                    dtype=np.float32)
            #print('Using single precision option')
        else:
            volume_buf = cl_array.zeros(self.cl_queue,
                                    (ny*nx*nz),
                                    dtype=np.float64)

        # Grab the light field image in sub-aperture mode
        samp = cl.Sampler(self.cl_ctx, False, cl.addressing_mode.CLAMP, cl.filter_mode.NEAREST)

        # Store the PSF in a CL 2d image texture, which will give us
        # some speedup in the algorithm since it caches texture accesses.
        lf_texture_volume = np.zeros((nt*ns, nu*nv), dtype=np.float32)
        for u in range(nu):
            for v in range(nv):
                lf_texture_volume[:,v*nu+u] = np.reshape(light_field.subaperture(u,v), (ns*nt), order='C')
        lf_texture_2d = cl.image_from_array(self.cl_ctx, lf_texture_volume.copy(), 1, 'r')

        # Set static kernel arguments
        kern = self.cl_prog.cl_backproject_wavespread
        kern.set_arg(0, lf_texture_2d)
        kern.set_arg(1, volume_buf.data)
        kern.set_arg(11, np.uint32(supersample_factor))
        kern.set_arg(12, samp)

        localSize = (self.WORKGROUP_X, self.WORKGROUP_Y)
        globalSize = (roundUp(nx//supersample_factor,self.WORKGROUP_X),
                      roundUp(ny//supersample_factor,self.WORKGROUP_Y))

        for z in range(nz):
            for x in range(supersample_factor):
                for y in range(supersample_factor):
                    coords = psf_coordinates[(x,y,z)]
                    coefficients = psf_coefficients[(x,y,z)]

                    # Extract the sorted coordinates. Copy here ensure
                    # "single segment" memory buffer, which seems to
                    # be required by cl.Buffer() below.
                    u_coords = coords[:,0].copy()
                    v_coords = coords[:,1].copy()
                    s_coords = coords[:,2].copy()
                    t_coords = coords[:,3].copy()
                    
                    u_coords_buf = cl.Buffer(self.cl_ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
                                             hostbuf = u_coords)
                    v_coords_buf = cl.Buffer(self.cl_ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
                                             hostbuf = v_coords)
                    s_coords_buf = cl.Buffer(self.cl_ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
                                             hostbuf = s_coords)
                    t_coords_buf = cl.Buffer(self.cl_ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
                                             hostbuf = t_coords)
                    coefficients_buf = cl.Buffer(self.cl_ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
                                                 hostbuf=coefficients)

                    kern.set_arg(2, u_coords_buf)
                    kern.set_arg(3, v_coords_buf)
                    kern.set_arg(4, s_coords_buf)
                    kern.set_arg(5, t_coords_buf)
                    kern.set_arg(6, coefficients_buf)
                    kern.set_arg(7, np.uint32(coefficients.shape[0])) # num_coefficients
                    kern.set_arg(8, np.uint32(z))  
                    kern.set_arg(9, np.uint32(x))  # dx
                    kern.set_arg(10, np.uint32(y))  # dy

                    # Execute the kernel
                    cl.enqueue_nd_range_kernel(self.cl_queue, kern, globalSize, localSize)
                
        # Download the result, and place the data for this subaperture into the lightfield
        volume = volume_buf.get(self.cl_queue)
        self.cl_queue.finish()
        vol = np.transpose(np.reshape(volume, (nz, ny, nx)),  (1, 2, 0))
        
        if self.postmultiplier is not None:
            return vol * self.postmultiplier
        else:
            return vol

    # ----------------------------------------------------------------------------
    #                          CPU IMPLEMENTATION
    # ----------------------------------------------------------------------------

    def backproject_cpu(self, light_field, zslice=None, use_sing_prec=False):
        """
        Using the given rayspread database, compute focused images at the
        given depths z_depths.

        Returns: A volume as a 3D numpy matrix that is indexed in [x,y,z]
        order.
        """
        # TODO: make rayspread functionality exist
        rayspreads = self.rayspread_db.rayspreads
        z_coords = self.rayspread_db.z_coords

        nx = self.rayspread_db.nx
        ny = self.rayspread_db.ny
        ns = self.rayspread_db.ns
        nt = self.rayspread_db.nt
        nu = self.rayspread_db.nu
        nv = self.rayspread_db.nv

        # Create an empty volume
        volume = np.zeros((ny, nx, len(z_coords)), dtype = np.float32)

        # if zslice is given, compute projection for only that slice
        if zslice is not None:
            z_keys = [ k for k in list(rayspreads.keys()) if k[0] == zslice ]
            rayspreads = extract( z_keys, rayspreads )

        # Accumulate data from the different z-slices, and add them into the lightfield.
        for spread_key in rayspreads:
            spread = rayspreads[spread_key]
            psf = spread[0]
            kernel_h_offset = spread[1]
            kernel_v_offset = spread[2]
            kernel_width = psf.shape[1]
            kernel_height = psf.shape[0]

            # Extract u,v,z
            z_idx = spread_key[0]
            u = spread_key[1]
            v = spread_key[2]

            # This performance shortcut avoids processing the rays
            # that are outside of the NA of the objective.  These rays
            # are vignetting and highly aberrated, and aren't so good
            # to use in any case.
            if (np.sqrt(np.power(u-(nu-1.0)/2.0,2) + np.power(v-(nv-1.0)/2.0,2)) >= nv/2.0):
                continue

            subaperture = light_field.subaperture(u, v)

            # zero-pad sub-aperture by half kernel width/height (otherwise splats will be cut off at
            # the left and top sizes!)
            ypad = kernel_height / 2  # setting these to 0 should disable zero padding
            xpad = kernel_width / 2 
            subaperture_pad = np.zeros((nt + 2*ypad, ns + 2*xpad))
            subaperture_pad[ ypad:ypad+nt , xpad:xpad+ns ] = subaperture

            output = filters.convolve(subaperture_pad, psf, mode='constant')

            # print "Shape: ", output.shape
            # print "Offsets: ", kernel_h_offset, kernel_v_offset
            # print "Dims: ", kernel_width, kernel_height

            # Numpy NDimage convolution crops the result
            # automatically, which removes half the kernel width and
            # height from the result.  We must adjust our kernel h and
            # v offset here to crop the output to the correct
            # dimensions.
            kernel_h_offset += kernel_width / 2
            kernel_v_offset += kernel_height / 2

            # Shift the result by the correct offset amount
            t_min = max(-kernel_v_offset,0)
            t_max = min(-kernel_v_offset+output.shape[0], output.shape[0])
            s_min = max(-kernel_h_offset,0)
            s_max = min(-kernel_h_offset+output.shape[1], output.shape[1])
            cropped_output = output[t_min:t_max, s_min:s_max]

            # Compute the opposite shift.  This is where we will sum the image in the output volume slice.
            t_min = max(kernel_v_offset,0)
            t_max = min(kernel_v_offset+output.shape[0], output.shape[0])
            s_min = max(kernel_h_offset,0)
            s_max = min(kernel_h_offset+output.shape[1], output.shape[1])
            try:
                volume_pad = np.zeros(subaperture_pad.shape)
                volume_pad[t_min:t_max, s_min:s_max] = cropped_output

                # undo zero padding
                volume[:,:,z_idx] += volume_pad[ ypad:ypad+nt , xpad:xpad+ns ]
            except ValueError:
                # Should only occur when the convolution places the
                # image out of bounds, which can happen at very high
                # NA.
                pass

        return volume

    def project_cpu(self, volume, zslice=None, use_sing_prec=False):
        """
        Using the given rayspread database, compute a light field by
        projecting the volume using rayspreads.

        Option zslice allows computing the light field corresponding 
        to a single z plane in the volume.

        Returns: A lightfield as a tiled set of sub-aperture
        (i.e. pinhole) images.
        """
        rayspreads = self.rayspread_db.flipped_rayspreads
        z_coords = self.rayspread_db.z_coords

        nx = self.rayspread_db.nx
        ny = self.rayspread_db.ny
        nu = self.rayspread_db.nu
        nv = self.rayspread_db.nv

        # Create an empty volume
        lf = np.zeros((self.rayspread_db.nv * ny, self.rayspread_db.nu * nx), dtype = np.float32)

        # if zslice is given, compute projection for only that slice
        if zslice is not None:
            z_keys = [ k for k in list(rayspreads.keys()) if k[0] == zslice ]
            rayspreads = extract( z_keys, rayspreads )

        # Accumulate data from the different z-slices, and add them into the lightfield.
        for spread_key, spread in list(rayspreads.items()):
            # Extract u,v,z
            z_idx = spread_key[0]
            u = spread_key[1]
            v = spread_key[2]

            # This performance shortcut avoids processing the rays
            # that are outside of the NA of the objective.  These rays
            # are vignetting and highly aberrated, and aren't so good
            # to use in any case.
            if (np.sqrt(np.power(u-(nu-1.0)/2.0,2) + np.power(v-(nv-1.0)/2.0,2)) >= nv/2.0):
                continue

            kernel_h_offset = spread[1]
            kernel_v_offset = spread[2]
            psf = spread[0]
            kernel_width = psf.shape[1]
            kernel_height = psf.shape[0]
            
            zslice = volume[:,:,z_idx]

            # zero-pad zslice by half kernel width/height (otherwise
            # splats will be cut off at the left and top sizes!)
            ypad = kernel_height / 2  # setting these to 0 should disable zero padding
            xpad = kernel_width / 2 
            
            zslice_pad = np.zeros((ny + ypad, nx + xpad))
            zslice_pad[ ypad: , xpad: ] = zslice
            
            output = filters.convolve(zslice_pad, psf, mode='constant')        

            # Numpy NDimage convolution crops the result
            # automatically, which removes half the kernel width and
            # height from the result.  We must adjust our kernel h and
            # v offset here to crop the output to the correct
            # dimensions.
            kernel_h_offset += kernel_width / 2
            kernel_v_offset += kernel_height / 2

            # Shift the result by the correct offset amount
            v_min = max(-kernel_v_offset,0)
            v_max = min(-kernel_v_offset+output.shape[0], output.shape[0])
            u_min = max(-kernel_h_offset,0)
            u_max = min(-kernel_h_offset+output.shape[1], output.shape[1])
            cropped_output = output[v_min:v_max, u_min:u_max]

            # Compute the opposite shift.  This is where we will sum the image in the sub-aperture.
            v_min = max(kernel_v_offset,0)
            v_max = min(kernel_v_offset+output.shape[0], output.shape[0])
            u_min = max(kernel_h_offset,0)
            u_max = min(kernel_h_offset+output.shape[1], output.shape[1])

            
            try:
                lf_subap_pad = np.zeros(zslice_pad.shape)
                lf_subap_pad[v_min:v_max, u_min:u_max] += cropped_output

                # undo zero padding
                lf_subap = lf_subap_pad[ ypad: , xpad: ]
            
                lf[v*ny:(v+1)*ny, u*nx:(u+1)*nx] += lf_subap
            except ValueError:
                # Should only occur when the convolution places the
                # image out of bounds, which can happen at very high
                # NA.
                pass

        return LightField(lf, self.rayspread_db.nu, self.rayspread_db.nv,
                          self.rayspread_db.ns, self.rayspread_db.nt,
                          representation = LightField.TILED_SUBAPERTURE)
