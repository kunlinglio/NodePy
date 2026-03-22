<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue';
import { useTableStore } from '@/stores/tableStore';
import { useModalStore } from '@/stores/modalStore';
import TableColumnEdit from './TableColumnEdit.vue';
//@ts-ignore
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiPlus, mdiClose } from '@mdi/js';

const props = defineProps<{
    data: any,
    noC: number,
    noR: number
}>();

const tableStore = useTableStore();
const modalStore = useModalStore();

// 单元格引用
const cellRefs = ref<HTMLDivElement[][]>([]);
// 输入框引用
const inputRefs = ref<HTMLInputElement[][]>([]);
// 列宽配置
const columnWidths = ref<number[]>([]);

// 当前编辑的单元格
const editingCell = ref<{ row: number; col: number } | null>(null);
const editValue = ref<string>('');

// 行号列宽
const rowHeaderWidth = 80;

/**
 * 格式化单元格显示值（Date 类型只显示 YYYY-MM-DD）
 */
function formatCellValue(value: any, colType: string): string {
    if (colType !== 'Datetime') {
        return value !== null && value !== undefined ? String(value) : '';
    }
    if (!value) return '';
    try {
        const date = new Date(value);
        if (!isNaN(date.getTime())) {
            return date.toISOString().split('T')[0]!;
        }
    } catch (e) {
        // 忽略解析错误
    }
    return String(value);
}

/**
 * 格式化编辑框初始值（Date 类型显示 YYYY-MM-DD）
 */
function formatEditValue(value: any, colType: string): string {
    if (colType !== 'Datetime') {
        return value !== null && value !== undefined ? String(value) : '';
    }
    if (!value) return '';
    try {
        const date = new Date(value);
        if (!isNaN(date.getTime())) {
            return date.toISOString().split('T')[0]!;
        }
    } catch (e) {}
    return String(value);
}

// 计算列宽（根据列名长度）
const calculateColumnWidths = () => {
    if (!tableStore.currentTableData.col_names?.length) return;
    
    const baseWidth = 100;
    const charWidth = 8;
    const minWidth = 80;
    const maxWidth = 300;
    
    columnWidths.value = tableStore.currentTableData.col_names.map(colName => {
        let width = baseWidth + (colName.length * charWidth);
        const colType = tableStore.currentTableData.col_types[colName] || 'str';
        width += colType.length * 6;
        width += 24; // 删除按钮宽度
        return Math.min(Math.max(width, minWidth), maxWidth);
    });
};

/**
 * 打开列编辑模态框（添加/修改列）
 */
function openColumnEditModal(
    mode: 'add' | 'modify',
    columnName: string,
    columnType: string,
    columnIndex?: number
) {
    const modalId = `column-edit-${Date.now()}`;
    const editWidth = 300;
    const editHeight = 350;
    modalStore.createModal({
        id: modalId,
        component: TableColumnEdit,
        title: mode === 'add' ? '添加列' : '修改列',
        isActive: true,
        isResizable: false,
        isDraggable: true,
        position:{
            x: window.innerWidth / 2 - editWidth / 2,
            y: window.innerHeight / 2 - editHeight / 2
        },
        size:{
            width: editWidth,
            height: editHeight
        },
        props: {
            initialName: columnName,
            initialType: columnType,
            onConfirm: (newName: string, newType: string) => {
                if (mode === 'add') {
                    tableStore.addColumn(newName, newType as any);
                    nextTick(() => calculateColumnWidths());
                } else if (mode === 'modify' && columnIndex !== undefined) {
                    const oldColName = tableStore.currentTableData.col_names[columnIndex]!;
                    // 更新列名（如果变化）
                    if (newName !== oldColName) {
                        tableStore.updateColumnName(oldColName, newName);
                    }
                    // 更新列类型（如果变化）
                    const currentType = tableStore.currentTableData.col_types[newName] || 'str';
                    if (newType !== currentType) {
                        tableStore.updateColumnType(newName, newType as any);
                    }
                    calculateColumnWidths();
                }
                modalStore.destroyModal(modalId);
            },
            onCancel: () => {
                modalStore.destroyModal(modalId);
            },
        },
    });
}

/**
 * 开始编辑单元格
 */
function startEditCell(rowIndex: number, colIndex: number) {
    const colName = tableStore.currentTableData.col_names[colIndex];
    const cellValue = tableStore.currentTableData.rows[rowIndex]?.[colName!];
    const colType = tableStore.currentTableData.col_types[colName!] || 'str';
    
    editingCell.value = { row: rowIndex, col: colIndex };
    editValue.value = formatEditValue(cellValue, colType);
    
    nextTick(() => {
        if (inputRefs.value[rowIndex]?.[colIndex]) {
            inputRefs.value[rowIndex][colIndex].focus();
            inputRefs.value[rowIndex][colIndex].select();
        }
    });
}

/**
 * 结束编辑单元格
 */
function finishEditCell() {
    if (!editingCell.value) return;
    
    const { row, col } = editingCell.value;
    const colName = tableStore.currentTableData.col_names[col]!;
    const colType = tableStore.currentTableData.col_types[colName];
    
    let finalValue: any = editValue.value.trim();
    
    // 处理空值
    if (finalValue === '' || finalValue === null || finalValue === undefined) {
        switch (colType) {
            case 'int':
            case 'float':
                finalValue = 0;
                break;
            case 'bool':
                finalValue = false;
                break;
            case 'str':
            case 'Datetime':
                finalValue = '';
                break;
            default:
                finalValue = null;
        }
    } else {
        try {
            switch (colType) {
                case 'int':
                    finalValue = parseInt(finalValue, 10);
                    if (isNaN(finalValue)) finalValue = 0;
                    break;
                case 'float':
                    finalValue = parseFloat(finalValue);
                    if (isNaN(finalValue)) finalValue = 0;
                    break;
                case 'bool':
                    finalValue = finalValue.toLowerCase() === 'true' || finalValue === '1';
                    break;
                case 'str':
                    break;
                case 'Datetime':
                    // 直接存储用户输入的字符串，不做转换
                    break;
            }
        } catch (error) {
            console.warn('值转换失败:', error);
            // 转换失败时设置默认值
            switch (colType) {
                case 'int':
                case 'float':
                    finalValue = 0;
                    break;
                case 'str':
                case 'Datetime':
                    finalValue = '';
                    break;
                case 'bool':
                    finalValue = false;
                    break;
                default:
                    finalValue = null;
            }
        }
    }
    
    tableStore.updateCell(row, colName, finalValue);
    editingCell.value = null;
}

/**
 * 取消编辑单元格
 */
function cancelEditCell() {
    editingCell.value = null;
}

/**
 * 处理按键事件
 */
function handleKeyDown(event: KeyboardEvent, rowIndex: number, colIndex: number) {
    if (!editingCell.value) return;
    
    switch (event.key) {
        case 'Enter':
            finishEditCell();
            if (rowIndex < tableStore.numRows - 1) {
                startEditCell(rowIndex + 1, colIndex);
            }
            event.preventDefault();
            break;
            
        case 'Tab':
            finishEditCell();
            if (colIndex < tableStore.numCols - 1) {
                startEditCell(rowIndex, colIndex + 1);
            } else if (rowIndex < tableStore.numRows - 1) {
                startEditCell(rowIndex + 1, 0);
            }
            event.preventDefault();
            break;
            
        case 'Escape':
            cancelEditCell();
            break;
            
        case 'ArrowUp':
            if (editingCell.value.row > 0) {
                finishEditCell();
                startEditCell(rowIndex - 1, colIndex);
                event.preventDefault();
            }
            break;
            
        case 'ArrowDown':
            if (editingCell.value.row < tableStore.numRows - 1) {
                finishEditCell();
                startEditCell(rowIndex + 1, colIndex);
                event.preventDefault();
            }
            break;
            
        case 'ArrowLeft':
            if (editingCell.value.col > 0) {
                finishEditCell();
                startEditCell(rowIndex, colIndex - 1);
                event.preventDefault();
            }
            break;
            
        case 'ArrowRight':
            if (editingCell.value.col < tableStore.numCols - 1) {
                finishEditCell();
                startEditCell(rowIndex, colIndex + 1);
                event.preventDefault();
            }
            break;
    }
}

/**
 * 选择单元格
 */
function selectCell(rowIndex: number, colIndex: number) {
    tableStore.selectedCell = { row: rowIndex, col: colIndex };
}

/**
 * 修改列（双击或右键列名触发）
 */
function modifyColumn(colIndex: number) {
    const colName = tableStore.currentTableData.col_names[colIndex]!;
    const colType = tableStore.currentTableData.col_types[colName] || 'str';
    openColumnEditModal('modify', colName, colType, colIndex);
}

/**
 * 在末尾添加新列
 */
function addColumnAtPosition() {
    const defaultName = `Column_${tableStore.numCols + 1}`;
    openColumnEditModal('add', defaultName, 'str');
}

// 初始化单元格引用数组和列宽
watch(() => [tableStore.numRows, tableStore.numCols], () => {
    cellRefs.value = Array(tableStore.numRows).fill(null).map(() => 
        Array(tableStore.numCols).fill(null)
    );
    inputRefs.value = Array(tableStore.numRows).fill(null).map(() => 
        Array(tableStore.numCols).fill(null)
    );
    calculateColumnWidths();
}, { immediate: true });

// 监听列名变化，重新计算列宽
watch(() => tableStore.currentTableData.col_names, () => {
    calculateColumnWidths();
}, { deep: true });

onMounted(() => {
    calculateColumnWidths();
});
</script>

<template>
    <div class="editable-table">
        <div class="table-container">
            <div class="table-wrapper">
                <!-- 列标题行 -->
                <div class="table-row header-row">
                    <div class="table-cell corner-cell">
                        <div class="column-header">
                            <span class="column-name">行号</span>
                        </div>
                    </div>
                    
                    <div 
                        v-for="(colName, colIndex) in tableStore.currentTableData.col_names" 
                        :key="`col-${colIndex}`"
                        class="table-cell header-cell column-header"
                        :style="{ width: columnWidths[colIndex] ? columnWidths[colIndex] + 'px' : '150px' }"
                        :title="`${colName} (${tableStore.currentTableData.col_types[colName] || 'str'})`"
                        @dblclick="modifyColumn(colIndex)"
                        @contextmenu.prevent="modifyColumn(colIndex)"
                    >
                        <div class="column-header-content">
                            <div class="column-header-text">
                                <span class="column-name">{{ colName }}</span>
                                <span class="column-type">{{ tableStore.currentTableData.col_types[colName] || 'str' }}</span>
                            </div>
                            <button 
                                class="delete-column-btn"
                                @click.stop="tableStore.deleteColumn(colIndex)"
                                :disabled="tableStore.numCols <= 1"
                                title="删除列"
                            >
                                <svg-icon :path="mdiClose" :size="22" type="mdi"></svg-icon>
                            </button>
                        </div>
                    </div>
                    
                    <div class="table-cell add-column-cell">
                        <button @click="addColumnAtPosition" title="添加列">
                            <svg-icon :path="mdiPlus" :size="22" type="mdi"></svg-icon>
                        </button>
                    </div>
                </div>
                
                <!-- 数据行 -->
                <div 
                    v-for="(row, rowIndex) in tableStore.currentTableData.rows" 
                    :key="`row-${rowIndex}`"
                    class="table-row data-row"
                    :class="{ 'selected-row': tableStore.selectedCell?.row === rowIndex }"
                >
                    <div class="table-cell row-header" :style="{ width: `${rowHeaderWidth}px` }">
                        <span class="row-number">{{ rowIndex + 1 }}</span>
                        <button 
                            class="delete-row-btn"
                            @click="tableStore.deleteRow(rowIndex)"
                            :disabled="tableStore.numRows <= 1"
                            title="删除行"
                        >
                            <svg-icon :path="mdiClose" :size="22" type="mdi"></svg-icon>
                        </button>
                    </div>
                    
                    <div 
                        v-for="(colName, colIndex) in tableStore.currentTableData.col_names" 
                        :key="`cell-${rowIndex}-${colIndex}`"
                        class="table-cell data-cell"
                        :style="{ width: columnWidths[colIndex] ? columnWidths[colIndex] + 'px' : '150px' }"
                        :class="{ 
                            'editing': editingCell?.row === rowIndex && editingCell?.col === colIndex,
                            'selected': tableStore.selectedCell?.row === rowIndex && tableStore.selectedCell?.col === colIndex
                        }"
                        :ref="el => {
                            if (cellRefs[rowIndex]) {
                                cellRefs[rowIndex][colIndex] = el as HTMLDivElement;
                            } else {
                                cellRefs[rowIndex] = [];
                                cellRefs[rowIndex][colIndex] = el as HTMLDivElement;
                            }
                        }"
                        @click="selectCell(rowIndex, colIndex)"
                        @dblclick="startEditCell(rowIndex, colIndex)"
                    >
                        <template v-if="!(editingCell?.row === rowIndex && editingCell?.col === colIndex)">
                            <span class="cell-content">
                                {{ formatCellValue(row[colName], tableStore.currentTableData.col_types[colName] || 'str') }}
                            </span>
                        </template>
                        
                        <template v-else>
                            <input
                                type="text"
                                v-model="editValue"
                                :ref="el => {
                                    if (inputRefs[rowIndex]) {
                                        inputRefs[rowIndex][colIndex] = el as HTMLInputElement;
                                    } else {
                                        inputRefs[rowIndex] = [];
                                        inputRefs[rowIndex][colIndex] = el as HTMLInputElement;
                                    }
                                }"
                                @blur="finishEditCell"
                                @keydown="(e) => handleKeyDown(e, rowIndex, colIndex)"
                                class="cell-input"
                            />
                        </template>
                    </div>
                </div>
                
                <!-- 添加行按钮 -->
                <div class="table-row add-row">
                    <div class="table-cell row-header add-row-cell">
                        <button @click="tableStore.addRow()" title="添加行">
                            <svg-icon :path="mdiPlus" :size="22" type="mdi"></svg-icon>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style lang="scss" scoped>
@use '@/common/global.scss' as *;

.editable-table {
    display: flex;
    flex: 1;
    flex-direction: column;
    height: 100%;
    width: 100%;
    overflow: auto;
    background: $background-color;
    border-radius: 10px;
    box-sizing: border-box;
}

.table-container {
    flex: 1;
    overflow: auto;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    background: #fff;
}

.table-wrapper {
    display: inline-block;
    min-width: 100%;
}

.table-row {
    display: flex;
    
    &.header-row {
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    &.data-row {
        &:hover {
            background: #f5f7fa;
        }
        
        &.selected-row {
            background: #e3f2fd;
        }
    }
}

.table-cell {
    border-right: 1px solid #ebeef5;
    border-bottom: 1px solid #ebeef5;
    min-height: 38px;
    box-sizing: border-box;
    padding: 6px 8px;
    overflow: hidden;
    display: flex;
    align-items: center;
    
    &.corner-cell {
        width: 80px;
        min-width: 80px;
        background-color: rgb(233, 236, 240);
        font-weight: 500;
        justify-content: center;
        position: sticky;
        left: 0;
        z-index: 5;
        
        .column-header {
            display: flex;
            flex-direction: column;
            gap: 4px;
            align-items: center;
            
            .column-name {
                font-weight: 600;
                color: #303133;
            }
        }
    }
    
    &.header-cell {
        font-weight: 600;
        text-align: center;
        background-color: rgb(235, 241, 245);
        user-select: none;
        cursor: pointer;
        position: relative;
        
        .column-header-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 4px;
            width: 100%;
            
            .column-header-text {
                display: flex;
                flex-direction: column;
                gap: 4px;
                align-items: center;
                flex: 1;
                overflow: hidden;
            }
            
            .column-name {
                flex: 1;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                color: #303133;
                font-weight: 600;
            }
            
            .column-type {
                font-size: 11px;
                color: #909399;
                font-weight: normal;
            }
            
            .delete-column-btn {
                padding: 0;
                font-size: 16px;
                border: none;
                background: transparent;
                color: #909399;
                cursor: pointer;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: all 0.2s;
                
                svg {
                    width: 16px;
                    height: 16px;
                }
                
                &:disabled {
                    opacity: 0.2;
                    cursor: not-allowed;
                }
            }
        }
    }
    
    &.row-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: rgb(233, 236, 240);
        user-select: none;
        flex-shrink: 0;
        font-weight: 500;
        color: #606266;
        position: sticky;
        left: 0;
        z-index: 5;
        
        .row-number {
            font-weight: 500;
            margin-left: 25px;
        }
        
        .delete-row-btn {
            padding: 0;
            font-size: 16px;
            border: none;
            background: transparent;
            color: #909399;
            cursor: pointer;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: all 0.2s;
            
            svg {
                width: 16px;
                height: 16px;
            }
            
            &:disabled {
                opacity: 0.2;
                cursor: not-allowed;
            }
        }
        
        &:hover .delete-row-btn {
            opacity: 1;
        }
    }
    
    &.data-cell {
        position: relative;
        cursor: pointer;
        word-break: break-word;
        white-space: normal;
        text-align: center;
        
        .cell-content {
            width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .cell-input {
            width: 100%;
            height: 100%;
            border: 1px solid #409eff;
            border-radius: 2px;
            padding: 4px 6px;
            font-size: inherit;
            box-sizing: border-box;
            outline: none;
            background: #fff;
        }
        
        &.editing {
            padding: 0;
        }
        
        &.selected {
            outline: 2px solid #409eff;
            outline-offset: -2px;
            z-index: 1;
        }
        
        &:hover {
            background: #f5f7fa;
        }
    }
    
    &.add-column-cell,
    &.add-row-cell {
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f5f7fa;
        cursor: pointer;
        flex-shrink: 0;
        
        button {
            width: 24px;
            height: 24px;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            color: #909399;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0;
            
            svg {
                width: 16px;
                height: 16px;
            }
            
            &:hover {
                background: #ecf5ff;
                border-color: #b3d8ff;
            }
        }
    }
}

.add-row {
    .add-row-cell {
        width: 80px;
    }
}
</style>