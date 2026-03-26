import AdminAuthenticatedServiceFactory from '@/utils/AdminAuthenticatedServiceFactory'
import { ApiError } from '@/utils/api';
import notify from '@/components/Notification/notify';
import { handleNetworkError } from '@/utils/networkError';
import { defineStore } from 'pinia'
export const useAdminStore = defineStore('admin', () => {
    const adminAuthService = AdminAuthenticatedServiceFactory.getService();
    async function getSystemStatus(){
        try{
            console.log('Fetching system status...')
            const response = await adminAuthService.getSystemStatsApiAdminStatsOverviewGet();
            console.log(response)
            return response;
        }
        catch(error){
            console.error('Error fetching system status:', error);
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
    async function getServerStorageStatus(limit: number = 10){
        try{
            console.log('Fetching server storage status...')
            const response = await adminAuthService.getTopStorageUsersApiAdminStatsStorageGet(limit);
            console.log(response)
            return response;
        }
        catch(error){
            console.error('Error fetching server storage status:', error);
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
                    case(422):
                        notify({
                            message: '验证错误',
                            type: 'error'
                        })
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
    async function getFinancialStatus(){
        try{
            console.log('Fetching financial status...')
            const reponse = await adminAuthService.getFinancialStatsApiAdminStatsFinancialGet();
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
    async function getProjectStatus(){
        try{
            console.log('Fetching project status...')
            const response = await adminAuthService.getProjectStatsApiAdminStatsProjectsGet();
            console.log(response)
            return response;
        }
        catch(error){
            console.error('Error fetching project status:', error);
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
    async function toggleProjectAccessible(id: number, show: boolean){
        try{
            console.log(`Toggling project ${id} accessible status to ${show}...`)
            const response = await adminAuthService.toggleProjectExploreApiAdminProjectsProjectIdToggleExplorePost(id,show);
            console.log(response)
            return response;
        }
        catch(error){
            console.error('Error toggling project accessible status:', error);
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
                    case(422):
                        notify({
                            message: '验证错误',
                            type: 'error'
                        })
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
            throw error;
        }
    }
    async function getSystemHealthStatus(){
        try{
            console.log('Fetching system health status...')
            const response = await adminAuthService.getSystemHealthApiAdminHealthGet();
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
    return{
        getSystemStatus,
        getServerStorageStatus,
        getFinancialStatus,
        getProjectStatus,
        toggleProjectAccessible,
        getSystemHealthStatus
    }
})