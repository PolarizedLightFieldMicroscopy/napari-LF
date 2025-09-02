import numpy as np
import time

# ----------------------------------------------------------------------------------------
#                            CONJUGATE GRADIENT SOLVER
# ----------------------------------------------------------------------------------------

def richardson_lucy_reconstruction(A, b, x0 = None,
                                   Rtol = 1e-6, NE_Rtol = 1e-6, max_iter = 100,
                                   sigmaSq = 0.0, beta = 0.0):
    '''
    Richardson-Lucy algorithm

    Ported from the RestoreTools MATLAB package available at:
    http://www.mathcs.emory.edu/~nagy/RestoreTools/

    Input: A  -  object defining the coefficient matrix.
           b  -  Right hand side vector.
 
     Optional Intputs:

           x0      - initial guess (must be strictly positive); default is x0 = A.T*b
           sigmaSq - the square of the standard deviation for the
                     white Gaussian read noise (variance)
           beta    - Poisson parameter for background light level  
           max_iter - integer specifying maximum number of iterations;
                      default is 100
           Rtol    - stopping tolerance for the relative residual,
                     norm(b - A*x)/norm(b)
                     default is 1e-6
           NE_Rtol - stopping tolerance for the relative residual,
                     norm(A.T*b - A.T*A*x)/norm(A.T*b)
                     default is 1e-6

    Output:
          x  -  solution

    Original MATLAB code by J. Nagy, August, 2011

    References:
    [1]  B. Lucy.
        "An iterative method for the rectication of observed distributions."
         Astronomical Journal, 79:745-754, 1974. 
    [2]  W. H. Richardson.
        "Bayesian-based iterative methods for image restoration.",
         J. Optical Soc. Amer., 62:55-59, 1972.
     [3]  C. R. Vogel.
        "Computational Methods for Inverse Problems",
        SIAM, Philadelphia, PA, 2002   


    '''

    # The A operator represents a large, sparse matrix that has dimensions [ nrays x nvoxels ]
    nrays = A.shape[0]
    nvoxels = A.shape[1]

    # Include read-noise variance offset here so b_norm is consistent
    b = np.nan_to_num(b, nan=0.0, posinf=0.0, neginf=0.0)
    b[b < 0] = 0.0
    if sigmaSq > 0:
        b = b + sigmaSq * np.ones(nrays, dtype=b.dtype)

    # Pre-compute some values for use in stopping criteria below
    b_norm = np.linalg.norm(b)
    if not np.isfinite(b_norm) or b_norm == 0:
        print("[DEBUG] b_norm non-finite or zero; forcing to 1.0 for scaling")
        b_norm = 1.0

    with np.errstate(all='ignore'):
        trAb = A.rmatvec(b)
    if not np.isfinite(trAb).all():
        bad = np.count_nonzero(~np.isfinite(trAb))
        raise FloatingPointError(f"A^T b produced {bad} non-finite values; operator is unhealthy.")

    # Variables defined below is not used.
    # trAb_norm = np.linalg.norm(trAb)

    # Start the optimization from the initial volume of a focal stack.
    if x0 is not None:
        x = x0
    else:
        x = trAb

    Rnrm = np.zeros(max_iter+1)
    Xnrm = np.zeros(max_iter+1)
    NE_Rnrm = np.zeros(max_iter+1)

    eps = np.spacing(1)
    tau = np.sqrt(eps)
    sigsq = tau
    minx = x.min()

    # If initial guess has negative values, compensate
    if minx < 0:
        x = x - min(0,minx) + sigsq

    with np.errstate(all='ignore'):
        normalization = A.rmatvec(np.ones(nrays)) + 1
    # Guard against division by zero in normalization
    normalization = np.maximum(normalization, tau)
    print(f"[DEBUG] Normalization: min={normalization.min()}, max={normalization.max()}")
    q = np.quantile(normalization, [0, 1e-6, 1e-4, 1e-2, 0.5, 0.98, 0.999, 0.9999, 1.0])
    print("\t    Normalization quantiles:", ", ".join(f"{v:.3g}" for v in q))

    # Initialize c; keep it strictly positive and finite
    with np.errstate(all='ignore'):
        c = A.matvec(x) + beta*np.ones(nrays) + sigmaSq*np.ones(nrays)
    c = np.where(np.isfinite(c), c, 0.0)
    c = np.maximum(c, tau)

    for i in range(max_iter):
        tic = time.time()
        x_prev = x.copy()

        # STEP 1: RL Update step
        ratio_b_to_c = b / c
        # Sanitize ratio to keep v finite
        ratio_b_to_c = np.where(np.isfinite(ratio_b_to_c), ratio_b_to_c, 0.0)
        with np.errstate(all='ignore'):
            v = A.rmatvec(ratio_b_to_c)
        if not np.isfinite(v).all():
            raise FloatingPointError("A^T (b/c) returned non-finite values; operator unhealthy.")
        x = (x * v) / normalization
        with np.errstate(all='ignore'):
            Ax = A.matvec(x)
        if not np.isfinite(Ax).all():
            raise FloatingPointError("A*x returned non-finite values; operator unhealthy.")
        residual = b - Ax
        c = Ax + beta*np.ones(nrays) + sigmaSq*np.ones(nrays)
        # Keep c strictly positive and finite to avoid non-finite values
        c = np.where(np.isfinite(c), c, 0.0)
        c = np.maximum(c, tau)

        # STEP 2: Compute residuals and check stopping criteria
        Rnrm[i] = np.linalg.norm(residual) / b_norm
        Xnrm[i] = np.linalg.norm(x - x_prev) / nvoxels
        #NE_Rnrm[i] = np.linalg.norm(trAb - A.rmatvec(Ax)) / trAb_norm # disabled for now to save on extra rmatvec

        toc = time.time()
        print('\t--> [ RL Iteration %d   (%0.2f seconds) ] ' % (i, toc-tic))
        print('\t      Residual Norm: %0.4g               (tol = %0.2e)  ' % (Rnrm[i], Rtol))
        #print '\t         Error Norm: %0.4g               (tol = %0.2e)  ' % (NE_Rnrm[i], NE_Rtol)
        print('\t        Update Norm: %0.4g                              ' % (Xnrm[i]))

        # stop because residual satisfies ||b-A*x|| / ||b||<= Rtol
        if Rnrm[i] <= Rtol:
            break

        # stop because normal equations residual satisfies ||A'*b-A'*A*x|| / ||A'b||<= NE_Rtol
        #if NE_Rnrm[i] <= NE_Rtol:
        #    break

    return x.astype(np.float32)

#---------------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
