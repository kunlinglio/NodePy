import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import Visitor from '@/views/Visitor.vue'
import Home from '@/views/Home.vue'
import File from '@/views//FileListView/File.vue'
import Project from '@/views/ProjectListView/ProjectList.vue'
import Login from '@/views/Login.vue'
import Example from '@/views/ExampleView/Example.vue'
import Editor from '@/views/Editor.vue'
import Explore from '@/views/Explore.vue'

const routes: Array<RouteRecordRaw> = [
    {
        path:'/',
        redirect:'/home'
    },
    {
        path: '/visitor',
        name: 'visitor',
        component: Visitor
    },
    {
        path: '/home',
        name: 'home',
        component: Home
    },
    {
        path: '/file',
        name: 'file',
        component: File
    },
    {
        path: '/project',
        name: 'project',
        component: Project
    },
    {
        path: '/login',
        name: 'login',
        component: Login
    },
    {
        path: '/example',
        name: 'example',
        component: Example
    },
    {
        path: '/example/:projectId',
        name: 'editor-example',
        component: Editor
    },
    {
        path: '/project/:projectId',
        name: 'editor-project',
        component: Editor
    },
    {
        path: '/explore/:docId?/:sectionIndex?',
        name: 'explore',
        component: Explore
    }
]

const router = createRouter({
    history: createWebHistory('/'),
    routes
})

export default router