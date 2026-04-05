import AdminAuthenticatedServiceFactory from '@/utils/AdminAuthenticatedServiceFactory'
import { ApiError } from '@/utils/api';
import notify from '@/components/Notification/notify';
import { handleNetworkError } from '@/utils/networkError';
import { defineStore } from 'pinia'
export const useAdminStore = defineStore('admin', () => {
    const adminAuthService = AdminAuthenticatedServiceFactory.getService();

    async function getUserNum(username?: (string|null)) {
        try {
            console.log('Fetching user number...')
            const response = await adminAuthService.listUsersNumApiAdminUsersListNumGet(username)
            console.log(response)
            return response
        } catch(err) {
            console.error('Error fetching user number:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 400:
                        notify({
                            message: '请求参数错误',
                            type: 'error'
                        });
                        break;
                    case 401:
                        notify({
                            message: '未认证',
                            type: 'error'
                        });
                        break;
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
            throw err
        }
    }

    async function getUserList(username?: (string | null), limit: number = 100, offset?: number) {
        try {
            console.log('Fetching user list...')
            const response = await adminAuthService.listUsersApiAdminUsersListGet(username, limit, offset)
            console.log(response)
            return response
        } catch(err) {
            console.error('Error fetching user list:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 400:
                        notify({
                            message: '请求参数错误',
                            type: 'error'
                        });
                        break;
                    case 401:
                        notify({
                            message: '未认证',
                            type: 'error'
                        });
                        break;
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
            throw err
        }
    }

    async function deleteUserAccount(userId: number) {
        try {
            console.log('Deleting user account...')
            await adminAuthService.deleteUserApiAdminUsersUserIdDelete(userId)
            notify({
                message: '用户账号删除成功',
                type: 'success'
            });
        } catch(err) {
            console.error('Error deleting user account:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
        }
    }

    async function resetUserPassword(userId: number, newPassword: string = 'default_password') {
        try {
            console.log('Resetting user password...')
            await adminAuthService.resetUserPasswordApiAdminUsersUserIdResetPasswordPost(userId, {
                new_password: newPassword
            })
            notify({
                message: '用户密码重置成功',
                type: 'success'
            })
        } catch(err) {
            console.error('Error resetting user password:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
        }
    }

    async function getStorageOverview() {
        try {
            console.log('Fetching storage overview...')
            const response = await adminAuthService.getOverviewApiAdminStorageOverviewGet()
            console.log(response)
            return response
        } catch(err) {
            console.error('Error fetching storage overview:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 401:
                        notify({
                            message: '未认证',
                            type: 'error'
                        });
                        break;
                    case 403:
                        notify({
                            message: '操作被禁止',
                            type: 'error'
                        });
                        break;
                    case 404:
                        notify({
                            message: '找不到用户',
                            type: 'error'
                        });
                        break;
                    case 500:
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        });
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
            throw err
        }
    }

    async function getUserStorage(userId: number) {
        try {
            console.log('Fetching user storage...')
            const response = await adminAuthService.getUserStorageApiAdminStorageUserUserIdGet(userId)
            console.log(response)
            return response
        } catch(err) {
            console.error('Error fetching user storage:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
            throw err
        }
    }

    async function getFileNum(filename?: (string|null)) {
        try {
            console.log('Fetching file number...')
            const response = await adminAuthService.listFilesNumApiAdminStorageFilesNumGet(filename)
            console.log(response)
            return response
        } catch(err) {
            console.error('Error fetching file number:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
            throw err
        }
    }

    async function getFileList(filename?: (string|null), limit: number = 100, offset?: number) {
        try {
            console.log('Fetching file list...')
            const response = await adminAuthService.listFilesApiAdminStorageFilesGet(filename, limit, offset)
            console.log(response)
            return response
        } catch(err) {
            console.error('Error fetching file list:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
            throw err
        }
    }

    async function previewFile(fileId: number) {
        try {
            console.log('Fetching file preview...')
            const reponse = await adminAuthService.previewFileApiAdminStorageFilesFileIdPreviewGet(fileId)
            console.log(reponse)
            return reponse
        } catch(err) {
            console.error('Error fetching file preview:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
            throw err
        }
    }

    async function deleteFile(fileId: number) {
        try {
            console.log('Deleting file...')
            await adminAuthService.deleteFileApiAdminStorageFilesFileIdDelete(fileId)
            notify({
                message: `文件${fileId}删除成功`,
                type: 'success'
            });
        } catch(err) {
            console.error('Error deleting file:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
        }
    }

    async function getFinancialStatus(){
        try{
            console.log('Fetching financial status...')
            const reponse = await adminAuthService.getFinancialStatsApiAdminFinancialOverviewGet();
            console.log(reponse)
            return reponse;
        }
        catch(error){
            console.error('Error fetching financial status:', error);
            if(error instanceof ApiError){
                switch(error.status){
                    case(401):
                        notify({
                            message: '未认证',
                            type: 'error'
                        });
                        break;
                    case(403):
                        notify({
                            message: '操作被禁止',
                            type: 'error'
                        });
                        break;
                    case(404):
                        notify({
                            message: '找不到用户',
                            type: 'error'
                        });
                        break;
                    case(500):
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        });
                        break;
                    default:
                        const errMsg = handleNetworkError(error)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                        }
                    }
            else{
                const errMsg = handleNetworkError(error)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
            throw error
        }
    }

    async function getProjectNum(ownerUsername?: (string|null), projectName?: (string|null)) {
        try {
            console.log('Fetching project number...')
            const response = await adminAuthService.listProjectsNumApiAdminProjectsOverviewNumGet(ownerUsername, projectName);
            console.log(response)
            return response;
        } catch(err) {
            console.error('Error fetching project number:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        })
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
            throw err
        }
    }

    async function getProjectList(ownerUsername?: (string|null), projectName?: (string|null), limit: number = 100, offset?: number) {
        try {
            console.log('Fetching project list...')
            const response = await adminAuthService.listProjectsApiAdminProjectsOverviewGet(ownerUsername, projectName, limit, offset);
            console.log(response)
            return response;
        } catch(err) {
            console.error('Error fetching project list:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        })
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
            throw err
        }
    }

    async function setProjectVisibility(projectId: number, show: boolean) {
        try {
            console.log(`Setting project visibility...`)
            await adminAuthService.setProjectVisibilityApiAdminProjectsProjectIdSetVisibilityPost(projectId, show);
            notify({
                message: `将项目 ${projectId} 的可见性设置为 ${show ? '公开' : '隐藏'}`,
                type: 'success'
            });
        } catch(err) {
            console.error('Error setting project visibility:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        })
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
        }
    }

    async function deleteProject(projectId: number) {
        try {
            console.log(`Deleting project ${projectId}...`)
            await adminAuthService.deleteProjectApiAdminProjectsProjectIdDelete(projectId)
            notify({
                message: `删除项目 ${projectId}`,
                type: 'success'
            });
        } catch(err) {
            console.error('Error deleting project:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        })
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
        }
    }


    async function getSystemHealthStatus(){
        try{
            console.log('Fetching system health status...')
            const response = await adminAuthService.getSystemHealthApiAdminHealthOverviewGet();
            console.log(response)
            return response;
        }
        catch(error){
            console.error('Error fetching system health status:', error);
            if(error instanceof ApiError){
                switch(error.status){
                    case(500):
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        });
                        break;
                    default:
                        const errMsg = handleNetworkError(error)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                        }
                    }
            else{
                const errMsg = handleNetworkError(error)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
            throw error
        }
    }

    async function getTutorialNum(tutorialId?: (number|null)) {
        try {
            console.log('Fetching tutorial review num...')
            const response = await adminAuthService.getTutorialReviewNumApiAdminTutorialsReviewsNumGet(tutorialId)
            console.log(response)
            return response;
        } catch(err) {
            console.error('Error fetching tutorial review num:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        })
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
            throw err
        }
    }

    async function getTutorialReview(tutorialId?: (number|null), limit: number = 100, offset?: number) {
        try {
            console.log('Fetching tutorial review list...')
            const response = await adminAuthService.getTutorialReviewApiAdminTutorialsReviewsGet(tutorialId, limit, offset)
            console.log(response)
            return response;
        } catch(err) {
            console.error('Error fetching tutorial review list:', err);
            if(err instanceof ApiError) {
                switch(err.status) {
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        })
                        break;
                    default:
                        const errMsg = handleNetworkError(err)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            } else {
                const errMsg = handleNetworkError(err)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
            throw err
        }
    }

    return{
        getUserNum,
        getUserList,
        deleteUserAccount,
        resetUserPassword,
        getStorageOverview,
        getUserStorage,
        getFileNum,
        getFileList,
        previewFile,
        deleteFile,
        getProjectNum,
        getProjectList,
        setProjectVisibility,
        deleteProject,
        getTutorialNum,
        getTutorialReview,
        getFinancialStatus,
        getSystemHealthStatus
    }
})