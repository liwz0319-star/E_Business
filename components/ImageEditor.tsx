
import React, { useState, useRef, useEffect } from 'react';

interface ImageEditorProps {
  image: any;
  onClose: () => void;
  onSave: (updatedImageUrl: string) => void;
}

type ToolType = 'crop' | 'text' | 'shapes' | 'brush' | null;

interface EditableElement {
  id: string;
  type: 'text' | 'shape';
  content?: string;
  shapeType?: string;
  x: number; // Top-left X %
  y: number; // Top-left Y %
  w: number; // Width %
  h: number; // Height %
  color: string;
  strokeWidth: number;
  fontSize: number;
  fontFamily: string;
  fontWeight?: string;
  fontStyle?: string;
}

interface HistoryState {
  elements: EditableElement[];
  paths: string[];
}

const ImageEditor: React.FC<ImageEditorProps> = ({ image, onClose, onSave }) => {
  const [activeTool, setActiveTool] = useState<ToolType>(null);
  const [zoom, setZoom] = useState(100);
  const [elements, setElements] = useState<EditableElement[]>([]);
  const [paths, setPaths] = useState<string[]>([]);
  
  const [history, setHistory] = useState<HistoryState[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  const [isDrawingBrush, setIsDrawingBrush] = useState(false);
  const [isMovingElement, setIsMovingElement] = useState(false);
  const [drawingPreview, setDrawingPreview] = useState<any>(null); 
  const [resizingHandle, setResizingHandle] = useState<string | null>(null);
  const [brushColor, setBrushColor] = useState('#101918');
  const [brushSize, setBrushSize] = useState(2);
  const [activeElementId, setActiveElementId] = useState<string | null>(null);
  const [selectedShapeToDraw, setSelectedShapeToDraw] = useState('rect');

  const [cropBox, setCropBox] = useState({ x: 20, y: 20, w: 60, h: 60 });
  const [cropDragMode, setCropDragMode] = useState<'move' | 'nw' | 'se' | null>(null);
  const [selectedCropRatio, setSelectedCropRatio] = useState<string>('free');

  const dragStartPos = useRef({ x: 0, y: 0 });
  const initialElementState = useRef<Partial<EditableElement>>({});
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  const tools = [
    { id: 'crop', icon: 'crop', label: '裁剪与旋转' },
    { id: 'text', icon: 'title', label: '添加文字' },
    { id: 'shapes', icon: 'category', label: '添加图形' },
    { id: 'brush', icon: 'brush', label: '画笔工具' },
  ];

  const shapesList = [
    { type: 'rect', icon: 'square', label: '矩形' },
    { type: 'circle', icon: 'circle', label: '圆形' },
    { type: 'triangle', icon: 'change_history', label: '三角形' },
    { type: 'star', icon: 'grade', label: '五角星' },
    { type: 'arrow', icon: 'arrow_forward', label: '箭头' },
    { type: 'chat', icon: 'chat_bubble', label: '气泡' },
  ];

  const fontFamilies = [
    { label: '极速雅黑', value: "'Plus Jakarta Sans', sans-serif" },
    { label: '时尚黑体', value: "'Inter', sans-serif" },
    { label: '人文宋体', value: "serif" },
    { label: '圆润萌体', value: "cursive" },
    { label: '代码等宽', value: "monospace" },
  ];

  const cropRatios = [
    { id: 'free', label: '自由比例', icon: 'aspect_ratio', value: null },
    { id: '1:1', label: '1:1 正方形', icon: 'square', value: 1 },
    { id: '4:3', label: '4:3 标准', icon: 'crop_landscape', value: 4/3 },
    { id: '3:4', label: '3:4 竖向', icon: 'crop_portrait', value: 3/4 },
    { id: '16:9', label: '16:9 宽屏', icon: 'crop_16_9', value: 16/9 },
    { id: '9:16', label: '9:16 故事', icon: 'crop_portrait', value: 9/16 },
  ];

  const activeElement = elements.find(el => el.id === activeElementId);

  const getPathData = (type: string) => {
    switch (type) {
      case 'rect': return `M 0 0 L 100 0 L 100 100 L 0 100 Z`;
      case 'circle': return `M 50 0 A 50 50 0 1 1 50 100 A 50 50 0 1 1 50 0`;
      case 'triangle': return `M 50 0 L 100 100 L 0 100 Z`;
      case 'star': return `M 50 0 L 61 35 L 98 35 L 68 57 L 79 91 L 50 70 L 21 91 L 32 57 L 2 35 L 39 35 Z`;
      case 'arrow': return `M 0 35 L 60 35 L 60 10 L 100 50 L 60 90 L 60 65 L 0 65 Z`;
      case 'chat': return `M 0 0 L 100 0 L 100 80 L 65 80 L 50 100 L 35 80 L 0 80 Z`;
      default: return '';
    }
  };

  const handleSetCropRatio = (ratioId: string, ratioValue: number | null) => {
    setSelectedCropRatio(ratioId);
    if (ratioValue === null || !imageRef.current) return;

    const img = imageRef.current;
    const imgRatio = img.naturalWidth / img.naturalHeight;
    
    let newW, newH;
    const targetRelativeRatio = ratioValue / imgRatio;

    if (targetRelativeRatio > 1) {
      newW = 90;
      newH = newW / targetRelativeRatio;
      if (newH > 90) {
        newH = 90;
        newW = newH * targetRelativeRatio;
      }
    } else {
      newH = 90;
      newW = newH * targetRelativeRatio;
      if (newW > 90) {
        newW = 90;
        newH = newW / targetRelativeRatio;
      }
    }

    setCropBox({
      x: (100 - newW) / 2,
      y: (100 - newH) / 2,
      w: newW,
      h: newH
    });
  };

  const saveToHistory = (newElements: EditableElement[], newPaths: string[]) => {
    const newSnap = { elements: [...newElements], paths: [...newPaths] };
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push(newSnap);
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
  };

  const handleUndo = () => {
    if (historyIndex > 0) {
      const prev = history[historyIndex - 1];
      setElements(prev.elements);
      setPaths(prev.paths);
      setHistoryIndex(historyIndex - 1);
    } else if (historyIndex === 0) {
      setElements([]);
      setPaths([]);
      setHistoryIndex(-1);
    }
  };

  const handleRedo = () => {
    if (historyIndex < history.length - 1) {
      const next = history[historyIndex + 1];
      setElements(next.elements);
      setPaths(next.paths);
      setHistoryIndex(historyIndex + 1);
    }
  };

  const addElementAt = (x: number, y: number, w: number, h: number, type: 'text' | 'shape', shapeType?: string) => {
    const id = Date.now().toString();
    const newEl: EditableElement = {
      id,
      type,
      content: type === 'text' ? '请输入文字' : '',
      shapeType,
      x,
      y,
      w: w || (type === 'text' ? 30 : 15), 
      h: h || (type === 'text' ? 6 : 5),   
      color: type === 'text' ? '#101918' : brushColor,
      strokeWidth: brushSize,
      fontSize: 24,
      fontFamily: "'Plus Jakarta Sans', sans-serif",
      fontWeight: 'bold',
      fontStyle: 'normal'
    };
    const updated = [...elements, newEl];
    setElements(updated);
    setActiveElementId(id);
    saveToHistory(updated, paths);
  };

  const updateActiveElement = (updates: Partial<EditableElement>) => {
    if (!activeElementId) return;
    const updated = elements.map(el => el.id === activeElementId ? { ...el, ...updates } : el);
    setElements(updated);
  };

  const handlePointerDown = (e: React.PointerEvent, id?: string, extra?: any) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;

    dragStartPos.current = { x: e.clientX, y: e.clientY };

    if (activeTool === 'crop' && extra) {
      setCropDragMode(extra);
      return;
    }

    if (activeTool === 'brush') {
      setIsDrawingBrush(true);
      const x = (e.clientX - rect.left) / (zoom / 100);
      const y = (e.clientY - rect.top) / (zoom / 100);
      setPaths([...paths, `M ${x} ${y}`]);
      return;
    }

    if (activeElementId && typeof extra === 'string' && extra.startsWith('handle-')) {
      e.stopPropagation();
      setResizingHandle(extra.replace('handle-', ''));
      initialElementState.current = { ...activeElement };
      return;
    }

    if (activeTool === 'shapes' && !id) {
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      setDrawingPreview({ startX: x, startY: y, currentX: x, currentY: y, type: selectedShapeToDraw });
      return;
    }

    if (id) {
      e.stopPropagation();
      setActiveElementId(id);
      setIsMovingElement(true);
      initialElementState.current = { ...elements.find(el => el.id === id) };
      return;
    }

    if (activeTool === 'text') {
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      addElementAt(x - 15, y - 3, 0, 0, 'text'); 
    } else {
      setActiveElementId(null);
    }
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;

    const dx = ((e.clientX - dragStartPos.current.x) / rect.width) * 100;
    const dy = ((e.clientY - dragStartPos.current.y) / rect.height) * 100;

    if (activeTool === 'crop' && cropDragMode) {
      const moveFactor = 0.2;
      const dXRaw = e.clientX - dragStartPos.current.x;
      const dYRaw = e.clientY - dragStartPos.current.y;
      const newBox = { ...cropBox };
      if (cropDragMode === 'move') {
        newBox.x = Math.max(0, Math.min(100 - newBox.w, newBox.x + dXRaw * moveFactor));
        newBox.y = Math.max(0, Math.min(100 - newBox.h, newBox.y + dYRaw * moveFactor));
      } else if (cropDragMode === 'nw') {
        newBox.x = Math.max(0, Math.min(newBox.x + newBox.w - 5, newBox.x + dXRaw * moveFactor));
        newBox.y = Math.max(0, Math.min(newBox.y + newBox.h - 5, newBox.y + dYRaw * moveFactor));
        newBox.w = Math.max(5, newBox.w - (newBox.x - cropBox.x));
        newBox.h = Math.max(5, newBox.h - (newBox.y - cropBox.y));
      } else if (cropDragMode === 'se') {
        newBox.w = Math.max(5, Math.min(100 - newBox.x, newBox.w + dXRaw * moveFactor));
        newBox.h = Math.max(5, Math.min(100 - newBox.y, newBox.h + dYRaw * moveFactor));
      }
      setCropBox(newBox);
      dragStartPos.current = { x: e.clientX, y: e.clientY };
      return;
    }

    if (isDrawingBrush && activeTool === 'brush') {
      const x = (e.clientX - rect.left) / (zoom / 100);
      const y = (e.clientY - rect.top) / (zoom / 100);
      const lastPath = paths[paths.length - 1];
      setPaths([...paths.slice(0, -1), `${lastPath} L ${x} ${y}`]);
      return;
    }

    if (drawingPreview) {
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      setDrawingPreview({ ...drawingPreview, currentX: x, currentY: y });
      return;
    }

    if (resizingHandle && activeElement) {
      const init = initialElementState.current as EditableElement;
      let newX = init.x; let newY = init.y; let newW = init.w; let newH = init.h;
      if (resizingHandle.includes('e')) newW = Math.max(1, init.w + dx);
      if (resizingHandle.includes('s')) newH = Math.max(1, init.h + dy);
      if (resizingHandle.includes('w')) {
        const delta = Math.min(dx, init.w - 1);
        newX = init.x + delta;
        newW = init.w - delta;
      }
      if (resizingHandle.includes('n')) {
        const delta = Math.min(dy, init.h - 1);
        newY = init.y + delta;
        newH = init.h - delta;
      }
      updateActiveElement({ x: newX, y: newY, w: newW, h: newH });
      return;
    }

    if (isMovingElement && activeElementId) {
      const init = initialElementState.current as EditableElement;
      updateActiveElement({ x: init.x + dx, y: init.y + dy });
    }
  };

  const handlePointerUp = () => {
    if (drawingPreview) {
      const { startX, startY, currentX, currentY, type } = drawingPreview;
      const w = Math.abs(currentX - startX);
      const h = Math.abs(currentY - startY);
      const x = Math.min(startX, currentX);
      const y = Math.min(startY, currentY);
      if (w > 0.5 && h > 0.5) {
        addElementAt(x, y, w, h, 'shape', type);
      }
      setDrawingPreview(null);
    }
    
    if (isDrawingBrush || isMovingElement || resizingHandle) {
      saveToHistory(elements, paths);
    }
    setIsDrawingBrush(false);
    setIsMovingElement(false);
    setResizingHandle(null);
    setCropDragMode(null);
  };

  const renderHandles = (id: string) => {
    if (activeElementId !== id) return null;
    const handles = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'];
    return handles.map(h => (
      <div
        key={h}
        onPointerDown={(e) => handlePointerDown(e, id, `handle-${h}`)}
        className={`absolute size-2.5 bg-white border border-primary shadow-sm z-50 pointer-events-auto cursor-${h === 'n' || h === 's' ? 'ns' : h === 'e' || h === 'w' ? 'ew' : h === 'nw' || h === 'se' ? 'nwse' : 'nesw'}-resize`}
        style={{
          top: h.includes('n') ? '0%' : h.includes('s') ? '100%' : '50%',
          left: h.includes('w') ? '0%' : h.includes('e') ? '100%' : '50%',
          transform: 'translate(-50%, -50%)',
        }}
      />
    ));
  };

  return (
    <div className="fixed inset-0 z-[60] bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 md:p-6 transition-all" onPointerUp={handlePointerUp}>
      <div className="bg-white dark:bg-[#1e293b] w-full max-w-[1300px] h-[90vh] rounded-2xl shadow-2xl overflow-hidden flex flex-col lg:flex-row border border-slate-200 dark:border-slate-800 relative transition-colors">
        
        {/* Unified Top Right Close Button */}
        <button 
          onClick={() => {
            if (activeTool) {
              setActiveTool(null);
            } else {
              onClose();
            }
          }} 
          className="absolute top-4 right-4 z-[70] p-2.5 rounded-full text-slate-400 hover:text-red-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all active:scale-95"
          title={activeTool ? "关闭当前工具" : "关闭编辑器"}
        >
          <span className="material-symbols-outlined text-[24px]">close</span>
        </button>

        {/* Left Side Compact Toolbar */}
        <div className="absolute left-4 top-1/2 -translate-y-1/2 z-[60] flex flex-col items-center gap-2 bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl shadow-xl border border-slate-100 dark:border-slate-700 rounded-2xl p-1.5 transition-all">
          {tools.map((tool) => (
            <button
              key={tool.id}
              onClick={() => { 
                setActiveTool(prev => prev === tool.id ? null : tool.id as ToolType); 
                setActiveElementId(null); 
              }}
              className={`p-3 rounded-xl transition-all group flex items-center justify-center ${activeTool === tool.id ? 'bg-primary text-slate-900 shadow-glow' : 'text-slate-400 hover:text-primary hover:bg-primary/5'}`}
              title={tool.label}
            >
              <span className="material-symbols-outlined text-[24px] group-active:scale-90 transition-transform">{tool.icon}</span>
            </button>
          ))}
        </div>

        <div 
          className={`flex-1 relative overflow-hidden flex items-center justify-center bg-[#f8fafc] dark:bg-slate-950 transition-all duration-500 ${activeTool ? 'lg:w-[calc(100%-350px)]' : 'w-full'} ${activeTool === 'shapes' ? 'cursor-crosshair' : ''}`}
          onPointerMove={handlePointerMove}
        >
          <div className="relative z-10 p-10 w-full h-full flex items-center justify-center pointer-events-none" ref={containerRef}>
            <div 
              ref={canvasRef}
              className="relative shadow-2xl bg-white dark:bg-slate-800 p-0.5 group/image select-none overflow-hidden pointer-events-auto"
              onPointerDown={(e) => handlePointerDown(e)}
              style={{ transform: `scale(${zoom / 100})` }}
            >
              <img ref={imageRef} alt="Canvas" className="max-w-full max-h-[65vh] object-contain pointer-events-none" src={image?.url || image} />
              
              {drawingPreview && (
                <div 
                  className="absolute pointer-events-none z-50 border border-dashed border-primary bg-primary/5"
                  style={{
                    left: `${Math.min(drawingPreview.startX, drawingPreview.currentX)}%`,
                    top: `${Math.min(drawingPreview.startY, drawingPreview.currentY)}%`,
                    width: `${Math.abs(drawingPreview.currentX - drawingPreview.startX)}%`,
                    height: `${Math.abs(drawingPreview.currentY - drawingPreview.startY)}%`,
                  }}
                />
              )}

              <div className="absolute inset-0 z-30 pointer-events-none">
                {elements.map((el) => (
                  <div
                    key={el.id}
                    onPointerDown={(e) => handlePointerDown(e, el.id)}
                    className={`absolute pointer-events-auto flex items-center justify-center transition-all ${activeElementId === el.id ? 'cursor-move border border-primary/50 bg-primary/5' : 'border border-transparent'}`}
                    style={{ left: `${el.x}%`, top: `${el.y}%`, width: `${el.w}%`, height: `${el.h}%` }}
                  >
                    {activeElementId === el.id && (
                      <button 
                        onPointerDown={(e) => e.stopPropagation()}
                        onClick={() => setElements(elements.filter(item => item.id !== el.id))}
                        className="absolute -top-3 -right-3 size-5 bg-red-500 text-white rounded-full flex items-center justify-center shadow-lg hover:bg-red-600 transition-colors z-[60] pointer-events-auto"
                      >
                        <span className="material-symbols-outlined text-xs font-bold">close</span>
                      </button>
                    )}
                    {renderHandles(el.id)}
                    {el.type === 'text' ? (
                      <div 
                        contentEditable 
                        suppressContentEditableWarning
                        className="w-full h-full outline-none text-center bg-transparent flex items-center justify-center break-all overflow-hidden" 
                        style={{ color: el.color, fontSize: `${el.fontSize}px`, fontFamily: el.fontFamily }}
                        onBlur={(e) => updateActiveElement({ content: e.target.innerText })}
                      >
                        {el.content}
                      </div>
                    ) : (
                      <svg className="w-full h-full overflow-visible" viewBox="0 0 100 100" preserveAspectRatio="none">
                        <path d={getPathData(el.shapeType!)} fill="none" stroke={el.color} strokeWidth={el.strokeWidth} vectorEffect="non-scaling-stroke" />
                      </svg>
                    )}
                  </div>
                ))}
              </div>

              {activeTool === 'crop' && (
                <div className="absolute inset-0 z-40 bg-black/50 pointer-events-auto">
                   <div onPointerDown={(e) => handlePointerDown(e, undefined, 'move')} className="absolute border-2 border-white shadow-[0_0_0_9999px_rgba(0,0,0,0.4)] cursor-move transition-all" style={{ left: `${cropBox.x}%`, top: `${cropBox.y}%`, width: `${cropBox.w}%`, height: `${cropBox.h}%` }}>
                      <div className="absolute inset-0 grid grid-cols-3 grid-rows-3 opacity-30 pointer-events-none">
                        {[...Array(8)].map((_, i) => <div key={i} className="border-[0.5px] border-white/50"></div>)}
                      </div>
                      <div onPointerDown={(e) => { e.stopPropagation(); handlePointerDown(e, undefined, 'nw'); }} className="absolute -top-2 -left-2 size-4 bg-white border border-primary rounded-sm cursor-nw-resize shadow-md"></div>
                      <div onPointerDown={(e) => { e.stopPropagation(); handlePointerDown(e, undefined, 'se'); }} className="absolute -bottom-2 -right-2 size-4 bg-white border border-primary rounded-sm cursor-se-resize shadow-md"></div>
                   </div>
                </div>
              )}

              <div className="absolute inset-0 z-20 pointer-events-none overflow-hidden">
                <svg className="w-full h-full overflow-visible">
                  {paths.map((p, i) => <path key={i} d={p} fill="none" stroke={brushColor} strokeWidth={brushSize} strokeLinecap="round" strokeLinejoin="round" />)}
                </svg>
              </div>
            </div>
          </div>

          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-3 bg-white/95 dark:bg-slate-800/95 backdrop-blur-md border border-slate-200/60 rounded-full px-5 py-2 shadow-xl z-20 text-slate-500 transition-all">
            <button onClick={() => setZoom(Math.max(25, zoom - 10))} className="hover:text-primary"><span className="material-symbols-outlined">remove</span></button>
            <span className="text-xs font-bold w-10 text-center font-mono">{zoom}%</span>
            <button onClick={() => setZoom(Math.min(300, zoom + 10))} className="hover:text-primary"><span className="material-symbols-outlined">add</span></button>
            <div className="w-px h-4 bg-slate-200 dark:bg-slate-700 mx-1"></div>
            <button onClick={handleUndo} disabled={historyIndex < 0} className={`p-1.5 ${historyIndex >= 0 ? 'hover:text-primary' : 'opacity-30'}`}><span className="material-symbols-outlined">undo</span></button>
            <button onClick={handleRedo} disabled={historyIndex >= history.length - 1} className={`p-1.5 ${historyIndex < history.length - 1 ? 'hover:text-primary' : 'opacity-30'}`}><span className="material-symbols-outlined">redo</span></button>
          </div>
        </div>

        {activeTool && (
          <div className="w-full lg:w-[350px] flex flex-col bg-white dark:bg-[#1e293b] border-l border-slate-100 dark:border-slate-800 relative z-20 shadow-xl transition-colors">
            <div className="flex items-center justify-between p-6 border-b border-slate-100 dark:border-slate-800 shrink-0">
              <h2 className="text-slate-900 dark:text-white text-lg font-black tracking-tight">属性设置</h2>
              {/* Sidebar close button removed and merged with main close button */}
            </div>

            <div className="flex-1 overflow-y-auto sidebar-scroll p-6 space-y-8">
              {activeTool === 'crop' && (
                <div className="space-y-6">
                  <div className="p-3 bg-primary/5 rounded-xl border border-primary/20 mb-4">
                    <p className="text-[10px] text-primary-dark font-black uppercase tracking-wider">裁剪比例</p>
                    <p className="text-xs text-slate-500 leading-relaxed mt-1">选择预设比例以快速调整裁剪框大小。</p>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {cropRatios.map((ratio) => (
                      <button 
                        key={ratio.id}
                        onClick={() => handleSetCropRatio(ratio.id, ratio.value)}
                        className={`flex flex-col items-center gap-2 p-4 rounded-xl border transition-all ${selectedCropRatio === ratio.id ? 'bg-primary/10 border-primary ring-1 ring-primary' : 'bg-slate-50 dark:bg-slate-800/30 border-slate-100 hover:border-primary/50'}`}
                      >
                        <span className={`material-symbols-outlined text-[24px] ${selectedCropRatio === ratio.id ? 'text-primary' : 'text-slate-400'}`}>{ratio.icon}</span>
                        <span className={`text-[11px] font-bold ${selectedCropRatio === ratio.id ? 'text-primary-dark' : 'text-slate-500'}`}>{ratio.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {activeTool === 'shapes' && (
                <div className="space-y-6">
                  <div className="p-3 bg-primary/5 rounded-xl border border-primary/20 mb-4">
                    <p className="text-[10px] text-primary-dark font-black uppercase tracking-wider">交互提示</p>
                    <p className="text-xs text-slate-500 leading-relaxed mt-1">在画布上拖拽绘制图形，选中后拖拽手柄可调整大小。</p>
                  </div>
                  <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest">形状选择</h3>
                  <div className="grid grid-cols-3 gap-3">
                    {shapesList.map((shape) => (
                      <button 
                        key={shape.type}
                        onClick={() => setSelectedShapeToDraw(shape.type)}
                        className={`aspect-square rounded-xl border flex flex-col items-center justify-center transition-all ${selectedShapeToDraw === shape.type ? 'bg-primary/10 border-primary ring-1 ring-primary' : 'bg-slate-50 dark:bg-slate-800/30 border-slate-100 hover:border-primary/50'}`}
                      >
                        <span className={`material-symbols-outlined text-[28px] ${selectedShapeToDraw === shape.type ? 'text-primary' : 'text-slate-400'}`}>{shape.icon}</span>
                        <span className={`text-[10px] mt-1 font-bold ${selectedShapeToDraw === shape.type ? 'text-primary-dark' : 'text-slate-400'}`}>{shape.label}</span>
                      </button>
                    ))}
                  </div>

                  <div className="pt-6 border-t border-slate-50 dark:border-slate-800 space-y-6">
                    <div>
                      <div className="flex justify-between items-center mb-3">
                        <label className="text-xs font-black text-slate-400 uppercase tracking-widest">边框粗细</label>
                        <span className="text-xs font-bold text-primary">{activeElement?.type === 'shape' ? activeElement.strokeWidth : brushSize}px</span>
                      </div>
                      <input type="range" min="1" max="20" value={activeElement?.type === 'shape' ? activeElement.strokeWidth : brushSize} onChange={(e) => {
                          const val = parseInt(e.target.value);
                          if (activeElementId && activeElement?.type === 'shape') updateActiveElement({ strokeWidth: val }); else setBrushSize(val);
                        }} className="w-full h-1.5 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-primary" />
                    </div>
                    <div>
                      <label className="text-xs font-black text-slate-400 uppercase tracking-widest block mb-4">边框颜色</label>
                      <div className="grid grid-cols-6 gap-2">
                        {['#101918', '#FFFFFF', '#81D8D0', '#FF0000', '#FFD700', '#4ECDC4'].map(c => (
                          <button key={c} onClick={() => { if (activeElementId) updateActiveElement({ color: c }); else setBrushColor(c); }} className={`size-8 rounded-full border shadow-sm transition-all ${ (activeElementId ? activeElement?.color : brushColor) === c ? 'ring-2 ring-primary ring-offset-2 scale-110' : ''}`} style={{ backgroundColor: c }} />
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTool === 'text' && (
                <div className="space-y-6">
                  <div className="p-3 bg-primary/5 rounded-xl border border-primary/20 mb-4">
                    <p className="text-[10px] text-primary-dark font-black uppercase tracking-wider">文本设置</p>
                    <p className="text-xs text-slate-500 leading-relaxed mt-1">在照片任意位置点击以生成文本框。您可以双击文本框直接编辑内容。</p>
                  </div>

                  <div>
                    <label className="text-xs font-black text-slate-400 uppercase tracking-widest block mb-4">字体选择</label>
                    <div className="flex flex-col gap-2">
                      {fontFamilies.map((font) => (
                        <button 
                          key={font.value}
                          onClick={() => updateActiveElement({ fontFamily: font.value })}
                          className={`w-full px-4 py-3 rounded-xl text-sm border text-left transition-all ${ (activeElement?.fontFamily === font.value) ? 'bg-primary/10 border-primary font-bold text-slate-900' : 'bg-slate-50 dark:bg-slate-800 border-slate-100 hover:border-primary/40'}`}
                          style={{ fontFamily: font.value }}
                        >
                          {font.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-3">
                      <label className="text-xs font-black text-slate-400 uppercase tracking-widest">文字大小</label>
                      <span className="text-xs font-bold text-primary">{activeElement?.fontSize || 24}px</span>
                    </div>
                    <input 
                      type="range" min="12" max="120" 
                      value={activeElement?.fontSize || 24} 
                      onChange={(e) => updateActiveElement({ fontSize: parseInt(e.target.value) })} 
                      className="w-full h-1.5 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-primary" 
                    />
                  </div>

                  <div>
                    <label className="text-xs font-black text-slate-400 uppercase tracking-widest block mb-4">文字颜色</label>
                    <div className="grid grid-cols-6 gap-2">
                      {['#101918', '#FFFFFF', '#81D8D0', '#FF0000', '#FFD700', '#4ECDC4'].map(c => (
                        <button 
                          key={c} 
                          onClick={() => updateActiveElement({ color: c })} 
                          className={`size-8 rounded-full border shadow-sm transition-all ${ (activeElement?.color === c) ? 'ring-2 ring-primary ring-offset-2 scale-110' : ''}`} 
                          style={{ backgroundColor: c }} 
                        />
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTool === 'brush' && (
                <div className="space-y-6">
                   <div>
                    <label className="text-xs font-black text-slate-400 uppercase tracking-widest block mb-4">画笔粗细</label>
                    <input type="range" min="1" max="50" value={brushSize} onChange={(e) => setBrushSize(parseInt(e.target.value))} className="w-full h-1.5 bg-slate-100 rounded-lg appearance-none accent-primary" />
                  </div>
                  <div>
                    <label className="text-xs font-black text-slate-400 uppercase tracking-widest block mb-4">颜色选择</label>
                    <div className="grid grid-cols-6 gap-2">
                      {['#101918', '#81D8D0', '#FF6B6B'].map(c => (
                        <button key={c} onClick={() => setBrushColor(c)} className={`size-8 rounded-full border ${brushColor === c ? 'ring-2 ring-primary ring-offset-2' : ''}`} style={{ backgroundColor: c }} />
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="p-6 border-t border-slate-100 dark:border-slate-800 shrink-0">
              <button onClick={() => onSave(image?.url || image)} className="w-full bg-primary hover:bg-[#68cdc4] active:scale-95 text-slate-900 font-black text-sm py-4 rounded-xl flex items-center justify-center gap-2 transition-all shadow-xl shadow-primary/20">
                <span className="material-symbols-outlined font-bold">check_circle</span> 确认并保存
              </button>
            </div>
          </div>
        )}
      </div>

      <style>{`
        .cursor-crosshair { cursor: crosshair; }
        .shadow-glow { box-shadow: 0 0 15px -3px rgba(129, 216, 208, 0.4); }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; height: 16px; width: 16px; border-radius: 50%; background: #81D8D0; border: 3px solid white; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
      `}</style>
    </div>
  );
};

export default ImageEditor;
