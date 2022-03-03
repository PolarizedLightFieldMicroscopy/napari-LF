import numpy as np
from scipy.sparse.linalg import lsqr


# ------------------------------- LSQR SOLVER ----------------------------------

def lsqr_reconstruction(A, b, tol, max_iter,
                        regularization_lambda,
                        initial_volume = None):

    # The A operator represents a large, sparse matrix that has dimensions [ nrays x nvoxels ]
    nrays = A.shape[0]
    nvoxels = A.shape[1]

    print('Calling LSQR solver... (lambda = %0.2g)' % (regularization_lambda))
    # from scipy.sparse.linalg import lsqr

    result = lsqr(A, b, damp = regularization_lambda, iter_lim = max_iter, show=True)
    return result[0].astype(np.float32)

#------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
