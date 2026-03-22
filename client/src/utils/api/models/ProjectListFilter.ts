/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ProjectListFilter = {
    tags?: Array<string>;
    search_keyword?: (string | null);
    ordered_by?: ProjectListFilter.ordered_by;
    ranging?: any[];
};
export namespace ProjectListFilter {
    export enum ordered_by {
        CREATED_AT = 'created_at',
        UPDATED_AT = 'updated_at',
        NAME = 'name',
    }
}

