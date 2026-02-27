<template>
    <div class="ColToIntNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="compute">列转整数</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="col">
                <div class="param-description" :class="{'node-has-paramerr': colHasErr.value}">
                    操作列
                </div>
                <NodepySelectMany
                    :options="colHint"
                    :default-selected="defaultSelectedCol"
                    @select-change="(e: any) => updateSimpleSelectMany(data.param, 'col', colHint, e)"
                    @clear-select="clearSelectCol"
                    class="nodrag"
                />
            </div>
            <div class="result_col">
                <div class="param-description" :class="{'node-has-paramerr': result_colHasErr.value}">
                    结果列
                </div>
                <NodepyStringInput 
                    v-model="result_col" 
                    @update-value="() => updateSimpleStringNumberBoolValue(data.param, 'result_col', result_col)" 
                    class="nodrag" 
                    placeholder="结果列名"
                />
            </div>
            <div class="method">
                <div class="param-description" :class="{'node-has-paramerr': methodHasErr.value}">
                    转换方法
                </div>
                <NodepySelectFew
                    :options="methodUi"
                    :default-selected="defaultSelectedMethod"
                    @select-change="(e: any) => updateSimpleSelectFew(data.param, 'method', method, e)"
                    class="nodrag"
                />
            </div>
            <div class="output-table port">
                <div class="output-port-description">
                    输出
                </div>
                <Handle id="table" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': outputTableHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import {ref, computed, watch} from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import { getInputType } from '../getInputType'
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import NodepySelectFew from '../tools/Nodepy-selectFew.vue'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import { updateSimpleStringNumberBoolValue, updateSimpleSelectMany, updateSimpleSelectFew } from '../updateParam'
    import type { ColToIntNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<ColToIntNodeData>>()
    const method = ["FLOOR", "CEIL", "ROUND"]
    const methodUi = ["下取整", "上取整", "四舍五入"]
    const defaultSelectedMethod = [method.indexOf(props.data.param.method)]
    const colHint = computed(() => {
        if(props.data.hint?.col_choices?.length === 0) return ['']
        return props.data.hint?.col_choices || ['']
    })
    const defaultSelectedCol = ref(colHint.value.indexOf(props.data.param.col))
    const result_col = ref(props.data.param.result_col)
    const table_type = computed(() => getInputType(props.id, 'table'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['table']?.type || 'default')
    const outputTableHasErr = computed(() => handleOutputError(props.id, 'table'))
    const errMsg = ref<string[]>([])
    const colHasErr = ref({
        id: 'col',
        value: false
    })
    const result_colHasErr = ref({
        id: 'result_col',
        value: false
    })
    const methodHasErr = ref({
        id: 'method',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })


    const clearSelectCol = (resolve: any) => {
        props.data.param.col = ''
        defaultSelectedCol.value = -1
        resolve()
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, colHasErr, result_colHasErr, methodHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .ColToIntNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .col, .result_col, .method {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>