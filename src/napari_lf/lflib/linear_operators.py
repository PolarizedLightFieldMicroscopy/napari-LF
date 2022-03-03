import numpy as np

from lflib.lightfield import LightField
from scipy.sparse.linalg import LinearOperator

#------------------------------------------------------------------------------------
#                 LINEAR OPERATORS FOR LIGHT FIELD RECONSTRUCTION
#------------------------------------------------------------------------------------

class ScaledLinearOperator(object):
    def __init__(self, A, scale_factor):
        self.A = A
        self.scale_factor = scale_factor

    def matvec(self, x):
        return self.A.matvec(x) * self.scale_factor

    def rmatvec(self, x):
        return self.A.rmatvec(x) * self.scale_factor

#------------------------------------------------------------------------------------

class LightFieldOperator(object):
    def __init__(self, sirt, db, use_sing_prec):
        self.sirt = sirt
        self.db = db
        self.use_sing_prec = use_sing_prec
        self.diagonalizer = None

    def matvec(self, vol_vec):
        vol = np.reshape(vol_vec, (self.db.ny, self.db.nx, self.db.nz))
        im = self.sirt.project(vol, use_sing_prec=self.use_sing_prec).asimage(representation = LightField.TILED_SUBAPERTURE)
        b = np.reshape(im, (im.shape[0]*im.shape[1]))
        if self.diagonalizer is None:
            return b
        else:
            return self.diagonalizer * b

    def rmatvec(self, lf_vec):
        if self.diagonalizer is None:
            lf = np.reshape(lf_vec, (self.db.nt*self.db.nv, self.db.ns*self.db.nu))
        else:
            lf = np.reshape(self.diagonalizer*lf_vec, (self.db.nt*self.db.nv, self.db.ns*self.db.nu))
        vol = self.sirt.backproject(LightField(lf, self.db.nu, self.db.nv, self.db.ns, self.db.nt,
                                          representation = LightField.TILED_SUBAPERTURE), use_sing_prec=self.use_sing_prec)
        return np.reshape(vol, (self.db.nx * self.db.ny * self.db.nz))

    def as_linear_operator(self, nrays, nvoxels):
        return LinearOperator((nrays, nvoxels),
                              matvec=self.matvec,
                              rmatvec=self.rmatvec,
                              dtype='float')

#------------------------------------------------------------------------------------

class NormalEquationLightFieldOperator(object):
    def __init__(self, sirt, db, weighting_matrix = None):
        self.sirt = sirt
        self.db = db
        if weighting_matrix is not None:
            self.weighting_matrix = np.reshape(weighting_matrix, (db.nv*db.nt, db.nu*db.ns))
        else:
            self.weighting_matrix = None

    def matvec(self, vol_vec):
        vol = np.reshape(vol_vec.astype(np.float32), (self.db.ny, self.db.nx, self.db.nz))
        lf = self.sirt.project(vol).asimage(representation = LightField.TILED_SUBAPERTURE)
        if self.weighting_matrix is not None:
            lf *= self.weighting_matrix
        vol = self.sirt.backproject(LightField(lf, self.db.nu, self.db.nv, self.db.ns, self.db.nt,
                                          representation = LightField.TILED_SUBAPERTURE))
        return np.reshape(vol, (self.db.nx * self.db.ny * self.db.nz))

#------------------------------------------------------------------------------------

class RegularizedNormalEquationLightFieldOperator(object):
    def __init__(self, sirt, db, regularization_lambda):
        self.sirt = sirt
        self.db = db
        self.regularization_lambda = regularization_lambda

    def matvec(self, vol_vec):
        input_vol = np.reshape(vol_vec.astype(np.float32), (self.db.ny, self.db.nx, self.db.nz))
        lf = self.sirt.project(input_vol).asimage(representation = LightField.TILED_SUBAPERTURE)
        output_vol = self.sirt.backproject(LightField(lf, self.db.nu, self.db.nv,
                                                      self.db.ns, self.db.nt,
                                                      representation = LightField.TILED_SUBAPERTURE))


        # L2-Norm Regularization
        output_vol += self.regularization_lambda * self.regularization_lambda * input_vol
        
        return np.reshape(output_vol, (self.db.nx * self.db.ny * self.db.nz))

#------------------------------------------------------------------------------------

class AugmentedLightFieldOperator(object):
    def __init__(self, sirt, db, rho, structure_matrix):
        self.sirt = sirt
        self.db = db
        self.rho = rho
        self.structure_matrix = structure_matrix

    def matvec(self, vol_vec ):

        # Compute A*x
        vol = np.reshape(vol_vec, (self.db.ny, self.db.nx, self.db.nz))
        im = self.sirt.project(vol).asimage(representation = LightField.TILED_SUBAPERTURE)
        im_vec = np.reshape(im, (im.shape[0]*im.shape[1]))

        # Add the L2-Norm regularization term
        if self.structure_matrix is not None:
            reg_vec = np.sqrt(self.rho) * self.structure_matrix * vol_vec
        else:
            reg_vec = np.sqrt(self.rho) * vol_vec

        return np.concatenate((im_vec, reg_vec), axis=0)

    def rmatvec(self, vec ):

        # Compute transpose(A)*x
        lf_vec_len = (self.db.ns*self.db.nt*self.db.nu*self.db.nv)
        lf_vec = vec[0:lf_vec_len]
        lf = np.reshape(lf_vec, (self.db.nt*self.db.nv, self.db.ns*self.db.nu))
        vol = self.sirt.backproject(LightField(lf, self.db.nu, self.db.nv, self.db.ns, self.db.nt,
                                               representation = LightField.TILED_SUBAPERTURE))
        vol_vec = np.reshape(vol, (self.db.nx * self.db.ny * self.db.nz))

        # Compute rho * reg_vec
        if self.structure_matrix is not None:
            reg_vec = np.sqrt(self.rho) * self.structure_matrix.T * vec[lf_vec_len:]
        else:
            reg_vec = np.sqrt(self.rho) * vec[lf_vec_len:]

        return vol_vec + reg_vec

#------------------------------------------------------------------------------------

if __name__ == "__main__":
    pass

#EOF
