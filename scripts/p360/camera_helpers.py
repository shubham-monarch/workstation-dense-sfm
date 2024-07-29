import numpy as np
from read_write_model import qvec2rotmat


class CameraHelpers: 
    """
    Helper class to provide camera transformation related functions
    """
    def __init__(self,
                 fx =  1093.2768,
                 fy =  1093.2768,
                 cx =  964.989,
                 cy =  569.276): 
        
        self.fx = fx
        self.fy = fy
        self.cx = cx
        self.cy = cy

    def cam_intrinsics(self):
        """ returns 3 * 3 camera intrinsics matrix """
        return np.array([
                            [self.fx,0 , self.cx], 
                            [0, self.fy, self.cy], 
                            [0 , 0, 1]
                        ]).astype(np.float64)

    def cam_extrinsics(self, img):
        """ returns 3 * 4 extrinsics matrix """
        from read_write_model import qvec2rotmat
        R = qvec2rotmat(img.qvec)
        t = img.tvec.reshape(3,-1)
        cam_Rt = np.concatenate((R,t), axis = 1)
        return cam_Rt
    
    def _cam_projection_matrix(K, R_t):
        """"returns 3 * 4 projection matrix"""
        return np.dot(K, R_t)    
        
