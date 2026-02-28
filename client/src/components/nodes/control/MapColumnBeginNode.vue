<template>
    <div class="MapColumnBeginNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="control">列映射起始</NodeTitle>
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
            <div class="output-remains port">
                <div class="output-port-description">
                    剩余列
                </div>
                <Handle id="remains" type="source" :position="Position.Right" :class="[`${remains_schema_type}-handle-color`, {'node-errhandle': outputRemainsHasErr}]"/>
            </div>
            <div class="output-cell port">
                <div class="output-port-description">
                    单元格
                </div>
                <Handle id="cell" type="source" :position="Position.Right" :class="[`${cell_schema_type}-handle-color`, {'node-errhandle': outputCellHasErr}]"/>
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
    import { updateSimpleSelectMany } from '../updateParam'
    import type { MapColumnBeginNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<MapColumnBeginNodeData>>()
    const colHint = computed(() => {
        if(props.data.hint?.col_choices?.length === 0) return ['']
        return props.data.hint?.col_choices || ['']
    })
    const defaultSelectedCol = ref(colHint.value.indexOf(props.data.param.col))
    const table_type = computed(() => getInputType(props.id, 'table'))
    const remains_schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['remains']?.type || 'default')
    const cell_schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['cell']?.type || 'default')
    const outputRemainsHasErr = computed(() => handleOutputError(props.id, 'remains'))
    const outputCellHasErr = computed(() => handleOutputError(props.id, 'cell'))
    const errMsg = ref<string[]>([])
    const colHasErr = ref({
        id: 'col',
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
        handleParamError(props.data.error, errMsg, colHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .MapColumnBeginNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .col {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
            .output-remains {
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>