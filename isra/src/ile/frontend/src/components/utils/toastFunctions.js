import {toast} from "react-toastify";

export const easyToast = function(res, mSuccess, mFailed){
    if(res.status === 200){
        toast.success(mSuccess,{position: "bottom-right"});
    }else{
        toast.error(mFailed, {position: "bottom-right"});
    }
};

export const successToast = function(mSuccess){
    toast.success(mSuccess, {position: "bottom-right"});
};

export const warnToast = function(mWarn){
    toast.warn(mWarn, {position: "bottom-right"});
};

export const failedToast = function(mFailed){
   toast.error(mFailed, {position: "bottom-right"});
};