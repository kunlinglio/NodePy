/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_upload_file_api_files_upload__project_id__post } from '../models/Body_upload_file_api_files_upload__project_id__post';
import type { DataView } from '../models/DataView';
import type { ExploreList } from '../models/ExploreList';
import type { File } from '../models/File';
import type { FileInfo } from '../models/FileInfo';
import type { FinancialSymbolStats } from '../models/FinancialSymbolStats';
import type { LoginRequest } from '../models/LoginRequest';
import type { Project } from '../models/Project';
import type { ProjectInfo } from '../models/ProjectInfo';
import type { ProjectList } from '../models/ProjectList';
import type { ProjectListFilter } from '../models/ProjectListFilter';
import type { ProjectSetting } from '../models/ProjectSetting';
import type { ProjUIState } from '../models/ProjUIState';
import type { ResetPasswordRequest } from '../models/ResetPasswordRequest';
import type { SignupRequest } from '../models/SignupRequest';
import type { StorageStats } from '../models/StorageStats';
import type { SystemHealthResponse } from '../models/SystemHealthResponse';
import type { Tag } from '../models/Tag';
import type { TaskResponse } from '../models/TaskResponse';
import type { TokenResponse } from '../models/TokenResponse';
import type { TutorialReviewStats } from '../models/TutorialReviewStats';
import type { UserFileList } from '../models/UserFileList';
import type { UserInfo } from '../models/UserInfo';
import type { UserStorageInfo } from '../models/UserStorageInfo';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * List Projects
     * List all projects for the current user.
     * @returns ProjectList List of projects retrieved successfully
     * @throws ApiError
     */
    public static listProjectsApiProjectListGet(): CancelablePromise<ProjectList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/project/list',
            errors: {
                500: `Internal server error`,
            },
        });
    }
    /**
     * Copy Project
     * Copy a read only project, and create a new project under the current user.
     * Return new project id.
     * @param projectId
     * @returns number Project copied successfully
     * @throws ApiError
     */
    public static copyProjectApiProjectCopyProjectIdPost(
        projectId: number,
    ): CancelablePromise<number> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/project/copy/{project_id}',
            path: {
                'project_id': projectId,
            },
            errors: {
                404: `Project not found`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Get Project
     * Get the full data structure of a project.
     * @param projectId
     * @returns Project Graph retrieved successfully
     * @throws ApiError
     */
    public static getProjectApiProjectProjectIdGet(
        projectId: number,
    ): CancelablePromise<Project> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/project/{project_id}',
            path: {
                'project_id': projectId,
            },
            errors: {
                403: `User has no access to this project`,
                404: `Project or graph not found`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Delete Project
     * Delete a project.
     * @param projectId
     * @returns void
     * @throws ApiError
     */
    public static deleteProjectApiProjectProjectIdDelete(
        projectId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/project/{project_id}',
            path: {
                'project_id': projectId,
            },
            errors: {
                403: `User has no access to this project`,
                404: `Project not found`,
                422: `Validation Error`,
                423: `Project is locked, it may be being edited by another process`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Create Project
     * Create a new project for a user.
     * Return project id.
     * @param requestBody
     * @returns number Project created successfully
     * @throws ApiError
     */
    public static createProjectApiProjectCreatePost(
        requestBody: ProjectSetting,
    ): CancelablePromise<number> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/project/create',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Project name already exists`,
                404: `User not found`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Get Project Setting
     * Get the settings of a project.
     * @param projectId
     * @returns ProjectSetting Project setting retrieved successfully
     * @throws ApiError
     */
    public static getProjectSettingApiProjectSettingProjectIdGet(
        projectId: number,
    ): CancelablePromise<ProjectSetting> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/project/setting/{project_id}',
            path: {
                'project_id': projectId,
            },
            errors: {
                403: `User has no access to this project`,
                404: `Project not found`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Update Project Setting
     * Update the settings of a project.
     * @param projectId
     * @param requestBody
     * @returns any Project setting updated successfully
     * @throws ApiError
     */
    public static updateProjectSettingApiProjectUpdateSettingPost(
        projectId: number,
        requestBody: ProjectSetting,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/project/update_setting',
            query: {
                'project_id': projectId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Project setting update failed`,
                403: `User has no access to this project`,
                404: `Project not found`,
                422: `Validation Error`,
                423: `Project is locked, it may be being edited by another process`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Sync Project Ui
     * Only save the ui of a project. Make sure the ui_state corresponds to the workflow in last sync.
     * @param projectId
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static syncProjectUiApiProjectSyncUiPost(
        projectId: number,
        requestBody: ProjUIState,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/project/sync_ui',
            query: {
                'project_id': projectId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Sync Project
     * Save a project to the database, if topology changed, enqueue a task to execute it.
     * If decide to execute, enqueues a Celery task. Use
     * the returned `task_id` to subscribe to the websocket status endpoint
     * `/nodes/status/{task_id}`.
     * @param requestBody
     * @returns TaskResponse Task accepted and running
     * @throws ApiError
     */
    public static syncProjectApiProjectSyncPost(
        requestBody: Project,
    ): CancelablePromise<TaskResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/project/sync',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Invalid thumbnail data`,
                403: `User has no access to this project`,
                404: `Project not found`,
                422: `Validation Error`,
                423: `Project is locked, it may be being edited by another process`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Upload File
     * Upload a file to a project. Return the saved file info.
     * @param projectId
     * @param nodeId
     * @param formData
     * @returns File File uploaded successfully
     * @throws ApiError
     */
    public static uploadFileApiFilesUploadProjectIdPost(
        projectId: number,
        nodeId: string,
        formData: Body_upload_file_api_files_upload__project_id__post,
    ): CancelablePromise<File> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/files/upload/{project_id}',
            path: {
                'project_id': projectId,
            },
            query: {
                'node_id': nodeId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                400: `Bad Request - invalid file or parameters`,
                403: `Forbidden - not allowed`,
                422: `Validation Error`,
                500: `Internal Server Error`,
                507: `Insufficient Storage - user storage limit exceeded`,
            },
        });
    }
    /**
     * List Files
     * @returns UserFileList List of files for the user
     * @throws ApiError
     */
    public static listFilesApiFilesListGet(): CancelablePromise<UserFileList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/files/list',
            errors: {
                404: `Not Found`,
                500: `Internal Server Error`,
            },
        });
    }
    /**
     * Get File Content
     * Get the content of a file by its key and project id.
     * The project id is used to verify the access permission.
     *
     * **important: if user want to re upload a file, you need to delete the old file first,
     * otherwise the file space may not be released.**
     * @param key
     * @returns any Binary file content
     * @throws ApiError
     */
    public static getFileContentApiFilesKeyGet(
        key: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/files/{key}',
            path: {
                'key': key,
            },
            errors: {
                403: `Forbidden - not allowed to access this file`,
                404: `File not found`,
                422: `Validation Error`,
                500: `Internal Server Error`,
            },
        });
    }
    /**
     * Get File Content Guest
     * Get the content of a file by its key and project id.
     * The project id is used to verify the access permission.
     *
     * **important: if user want to re upload a file, you need to delete the old file first,
     * otherwise the file space may not be released.**
     * @param key
     * @returns any Binary file content
     * @throws ApiError
     */
    public static getFileContentGuestApiFilesGuestKeyGet(
        key: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/files/guest/{key}',
            path: {
                'key': key,
            },
            errors: {
                403: `Forbidden - not allowed to access this file`,
                404: `File not found`,
                422: `Validation Error`,
                500: `Internal Server Error`,
            },
        });
    }
    /**
     * Get Node Data
     * Get the data generated by a node.
     * @param dataId
     * @returns DataView Data retrieved successfully
     * @throws ApiError
     */
    public static getNodeDataApiDataDataIdGet(
        dataId: number,
    ): CancelablePromise<DataView> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/data/{data_id}',
            path: {
                'data_id': dataId,
            },
            errors: {
                403: `User has no access to this data`,
                404: `Project or Data not found`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Get Node Data Guest
     * Get the data generated by a node.
     * @param dataId
     * @returns DataView Data retrieved successfully
     * @throws ApiError
     */
    public static getNodeDataGuestApiDataGuestDataIdGet(
        dataId: number,
    ): CancelablePromise<DataView> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/data/guest/{data_id}',
            path: {
                'data_id': dataId,
            },
            errors: {
                403: `User has no access to this data`,
                404: `Project or Data not found`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Signup
     * sign up a new user, return a JWT token (no need to login again)
     * @param requestBody
     * @returns TokenResponse Successful Response
     * @returns any User created successfully
     * @throws ApiError
     */
    public static signupApiAuthSignupPost(
        requestBody: SignupRequest,
    ): CancelablePromise<TokenResponse | any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/auth/signup',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Username or email already registered`,
                422: `Invalid username or password`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Login
     * Login user and return JWT tokens
     * @param requestBody
     * @returns TokenResponse Login successful
     * @throws ApiError
     */
    public static loginApiAuthLoginPost(
        requestBody: LoginRequest,
    ): CancelablePromise<TokenResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/auth/login',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                401: `Invalid username or password`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Refresh Access Token
     * Use Refresh Token to get a new Access Token if access token expired
     * @returns TokenResponse Access token refreshed successfully
     * @throws ApiError
     */
    public static refreshAccessTokenApiAuthRefreshPost(): CancelablePromise<TokenResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/auth/refresh',
            errors: {
                401: `Invalid refresh token`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Logout
     * Logout user by clearing the Refresh Token
     * @returns string Logged out successfully
     * @throws ApiError
     */
    public static logoutApiAuthLogoutPost(): CancelablePromise<Record<string, string>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/auth/logout',
        });
    }
    /**
     * Get Explore Projects
     * Get the list of projects that are marked as 'show in explore'.
     * @param requestBody
     * @returns ExploreList Successful Response
     * @throws ApiError
     */
    public static getExploreProjectsApiExploreProjectsPost(
        requestBody: ProjectListFilter,
    ): CancelablePromise<ExploreList> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/explore/projects',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Explore Projects Num
     * Get the number of projects that are marked as 'show in explore'.
     * @param requestBody
     * @returns number Successful Response
     * @throws ApiError
     */
    public static getExploreProjectsNumApiExploreProjectsNumPost(
        requestBody: ProjectListFilter,
    ): CancelablePromise<number> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/explore/projects/num',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Current User Info
     * Get current authenticated user's information.
     * @returns any Current user information retrieved successfully
     * @throws ApiError
     */
    public static getCurrentUserInfoApiUserMeGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/user/me',
            errors: {
                401: `Unauthorized`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * List Tags
     * @returns Tag List of tags retrieved successfully
     * @throws ApiError
     */
    public static listTagsApiTagListGet(): CancelablePromise<Array<Tag>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/tag/list',
            errors: {
                500: `Internal server error`,
            },
        });
    }
    /**
     * Create Tags
     * @param tagName
     * @returns any Tag created successfully
     * @throws ApiError
     */
    public static createTagsApiTagCreatePost(
        tagName: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/tag/create',
            query: {
                'tag_name': tagName,
            },
            errors: {
                400: `Tag name duplicate`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Get Playground Project
     * Get a project for playground. Only allows projects owned by NodePy-Learning that are public.
     * Forks the project under the GUEST user automatically.
     * @param projectId
     * @returns Project Graph retrieved successfully
     * @throws ApiError
     */
    public static getPlaygroundProjectApiPlaygroundProjectIdGet(
        projectId: number,
    ): CancelablePromise<Project> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/playground/{project_id}',
            path: {
                'project_id': projectId,
            },
            errors: {
                403: `Project is not a public example`,
                404: `Project not found`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Sync Playground Project
     * Execute a project in playground mode.
     * The project should already be a forked temporary project (owned by GUEST or the current user).
     * Changes are saved to the temporary project before execution.
     * @param requestBody
     * @returns TaskResponse Task accepted and running
     * @throws ApiError
     */
    public static syncPlaygroundProjectApiPlaygroundSyncPost(
        requestBody: Project,
    ): CancelablePromise<TaskResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/playground/sync',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Invalid thumbnail data`,
                403: `Project is not a public example`,
                404: `Project not found`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Login
     * Login user and return JWT tokens
     * @param requestBody
     * @returns TokenResponse Login successful
     * @throws ApiError
     */
    public static loginApiAdminAuthLoginPost(
        requestBody: LoginRequest,
    ): CancelablePromise<TokenResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/admin/auth/login',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                401: `Invalid username or password`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Refresh Access Token
     * Use Refresh Token to get a new Access Token if access token expired
     * @returns TokenResponse Access token refreshed successfully
     * @throws ApiError
     */
    public static refreshAccessTokenApiAdminAuthRefreshPost(): CancelablePromise<TokenResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/admin/auth/refresh',
            errors: {
                401: `Invalid refresh token`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Logout
     * Logout user by clearing the Refresh Token
     * @returns string Logged out successfully
     * @throws ApiError
     */
    public static logoutApiAdminAuthLogoutPost(): CancelablePromise<Record<string, string>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/admin/auth/logout',
        });
    }
    /**
     * Get System Health
     * Combined health check and detailed performance stats.
     * Returns comprehensive metrics for FastAPI, Postgres, Redis, MinIO, and Celery.
     * @returns SystemHealthResponse Successful Response
     * @throws ApiError
     */
    public static getSystemHealthApiAdminHealthOverviewGet(): CancelablePromise<SystemHealthResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/admin/health/overview',
        });
    }
    /**
     * List Users
     * List all registered users, supports username search.
     * @param username
     * @param limit
     * @param offset
     * @returns UserInfo Successful Response
     * @throws ApiError
     */
    public static listUsersApiAdminUsersListGet(
        username?: (string | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<Array<UserInfo>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/admin/users/list',
            query: {
                'username': username,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                400: `Bad request`,
                401: `Unauthorized`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Users Num
     * Return the number of registered users, supports username search.
     * @param username
     * @returns number Successful Response
     * @throws ApiError
     */
    public static listUsersNumApiAdminUsersListNumGet(
        username?: (string | null),
    ): CancelablePromise<number> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/admin/users/list/num',
            query: {
                'username': username,
            },
            errors: {
                400: `Bad request`,
                401: `Unauthorized`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete User
     * Delete a user account.
     * @param userId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteUserApiAdminUsersUserIdDelete(
        userId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/admin/users/{user_id}',
            path: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Reset User Password
     * Reset a user's password to a provided new password.
     * @param userId
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static resetUserPasswordApiAdminUsersUserIdResetPasswordPost(
        userId: number,
        requestBody: ResetPasswordRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/admin/users/{user_id}/reset-password',
            path: {
                'user_id': userId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Financial Stats
     * Monitor financial data health and crawler coverage by aggregating
     * actual records and comparing with tracking status.
     * @returns FinancialSymbolStats Successful Response
     * @throws ApiError
     */
    public static getFinancialStatsApiAdminFinancialOverviewGet(): CancelablePromise<Array<FinancialSymbolStats>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/admin/financial/overview',
        });
    }
    /**
     * List Projects
     * List projects, supports owner username and project name filters.
     * @param ownerUsername
     * @param projectName
     * @param limit
     * @param offset
     * @returns ProjectInfo Successful Response
     * @throws ApiError
     */
    public static listProjectsApiAdminProjectsOverviewGet(
        ownerUsername?: (string | null),
        projectName?: (string | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<Array<ProjectInfo>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/admin/projects/overview',
            query: {
                'owner_username': ownerUsername,
                'project_name': projectName,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Projects Num
     * List projects, supports owner username and project name filters.
     * @param ownerUsername
     * @param projectName
     * @returns number Successful Response
     * @throws ApiError
     */
    public static listProjectsNumApiAdminProjectsOverviewNumGet(
        ownerUsername?: (string | null),
        projectName?: (string | null),
    ): CancelablePromise<number> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/admin/projects/overview/num',
            query: {
                'owner_username': ownerUsername,
                'project_name': projectName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Set Project Visibility
     * Set project public/private (show_in_explore).
     * @param projectId
     * @param show
     * @returns any Successful Response
     * @throws ApiError
     */
    public static setProjectVisibilityApiAdminProjectsProjectIdSetVisibilityPost(
        projectId: number,
        show: boolean,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/admin/projects/{project_id}/set-visibility',
            path: {
                'project_id': projectId,
            },
            query: {
                'show': show,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Project
     * Delete a project.
     * @param projectId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteProjectApiAdminProjectsProjectIdDelete(
        projectId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/admin/projects/{project_id}',
            path: {
                'project_id': projectId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Overview
     * Get storage stats of whole server.
     * @returns StorageStats Storage stats retrieved successfully
     * @throws ApiError
     */
    public static getOverviewApiAdminStorageOverviewGet(): CancelablePromise<StorageStats> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/admin/storage/overview',
            errors: {
                401: `Unauthorized`,
                403: `Access denied`,
                404: `User not found`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Get User Storage
     * Return a user's storage quota and usage details.
     * @param userId
     * @returns UserStorageInfo Successful Response
     * @throws ApiError
     */
    public static getUserStorageApiAdminStorageUserUserIdGet(
        userId: number,
    ): CancelablePromise<UserStorageInfo> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/admin/storage/user/{user_id}',
            path: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Files
     * List files, supports filename search.
     * @param filename
     * @param limit
     * @param offset
     * @returns FileInfo Successful Response
     * @throws ApiError
     */
    public static listFilesApiAdminStorageFilesGet(
        filename?: (string | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<Array<FileInfo>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/admin/storage/files',
            query: {
                'filename': filename,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Files Num
     * Return the number of files, supports filename search.
     * @param filename
     * @returns number Successful Response
     * @throws ApiError
     */
    public static listFilesNumApiAdminStorageFilesNumGet(
        filename?: (string | null),
    ): CancelablePromise<number> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/admin/storage/files/num',
            query: {
                'filename': filename,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Preview File
     * Get the content of a file by its key.
     * @param fileKey
     * @returns any Successful Response
     * @throws ApiError
     */
    public static previewFileApiAdminStorageFilesFileKeyPreviewGet(
        fileKey: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/admin/storage/files/{file_key}/preview',
            path: {
                'file_key': fileKey,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete File
     * Soft-delete a file record and attempt to remove from MinIO.
     * @param fileId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteFileApiAdminStorageFilesFileIdDelete(
        fileId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/admin/storage/files/{file_id}',
            path: {
                'file_id': fileId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Tutorial Review
     * Return like/dislike counts grouped by tutorial id.
     * @param tutorialId
     * @param limit
     * @param offset
     * @returns TutorialReviewStats Successful Response
     * @throws ApiError
     */
    public static getTutorialReviewApiAdminTutorialsReviewsGet(
        tutorialId?: (number | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<Array<TutorialReviewStats>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/admin/tutorials/reviews',
            query: {
                'tutorial_id': tutorialId,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Tutorial Review Num
     * Return the number of reviews for a specific tutorial.
     * @param tutorialId
     * @returns number Successful Response
     * @throws ApiError
     */
    public static getTutorialReviewNumApiAdminTutorialsReviewsNumGet(
        tutorialId?: (number | null),
    ): CancelablePromise<number> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/admin/tutorials/reviews/num',
            query: {
                'tutorial_id': tutorialId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Review Tutorial
     * @param tutorialId
     * @param review
     * @returns any Review tutorial successfully
     * @throws ApiError
     */
    public static reviewTutorialApiTutorialReviewTutorialIdPost(
        tutorialId: number,
        review: 'like' | 'dislike',
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/tutorial/review/{tutorial_id}',
            path: {
                'tutorial_id': tutorialId,
            },
            query: {
                'review': review,
            },
            errors: {
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Get Tutorial Reviews
     * Returns (like_count, dislike_count) for the given tutorial_id
     * @param tutorialId
     * @returns any[] Get tutorial reviews successfully
     * @throws ApiError
     */
    public static getTutorialReviewsApiTutorialReviewTutorialIdGet(
        tutorialId: number,
    ): CancelablePromise<any[]> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/tutorial/review/{tutorial_id}',
            path: {
                'tutorial_id': tutorialId,
            },
            errors: {
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Spa Fallback
     * @param fullPath
     * @returns any Successful Response
     * @throws ApiError
     */
    public static spaFallbackFullPathGet(
        fullPath: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/{full_path}',
            path: {
                'full_path': fullPath,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
