
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
  x: number;
  y: number;
  color: string;
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
  
  // History management
  const [history, setHistory] = useState<HistoryState[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  // Interaction states
  const [isDrawing, setIsDrawing] = useState(false);
  const [brushColor, setBrushColor] = useState('#81D8D0');
  const [brushSize, setBrushSize] = useState(5);
  const [activeElementId, setActiveElementId] = useState<string | null>(null);

  // Crop states (percentages)
  const [cropBox, setCropBox] = useState({ x: 20, y: 20, w: 60, h: 60 });
  const [cropDragMode, setCropDragMode] = useState<'move' | 'nw' | 'ne' | 'sw' | 'se' | null>(null);

  // General Dragging state
  const [isDragging, setIsDragging] = useState(false);
  const dragStartPos = useRef({ x: 0, y: 0 });
  const elementRefs = useRef<Record<string, HTMLDivElement | null>>({});
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLDivElement>(null);

  const tools = [
    { id: 'crop', icon: 'crop', label: '裁剪与旋转' },
    { id: 'text', icon: 'title', label: '添加文字' },
    { id: 'shapes', icon: 'shapes', label: '图形' },
    { id: 'brush', icon: 'brush', label: '画笔工具' },
  ];

  const fontFamilies = [
    { name: 'Jakarta Sans', value: "'Plus Jakarta Sans', sans-serif" },
    { name: 'Manrope', value: "'Manrope', sans-serif" },
    { name: 'Inter', value: "'Inter', sans-serif" },
    { name: '衬线体 (Serif)', value: "Georgia, serif" },
    { name: '等宽体 (Mono)', value: "'Courier New', monospace" },
  ];

  const shapesList = [
    { type: 'rect', icon: 'square' },
    { type: 'circle', icon: 'circle' },
    { type: 'triangle', icon: 'change_history' },
    { type: 'star', icon: 'grade' },
  ];

  const activeElement = elements.find(el => el.id === activeElementId);

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

  const addElementAt = (xPercent: number, yPercent: number, type: 'text' | 'shape', shapeType?: string) => {
    const id = Date.now().toString();
    const newEl: EditableElement = {
      id,
      type,
      content: type === 'text' ? '点击输入文字' : '',
      shapeType,
      x: xPercent,
      y: yPercent,
      color: type === 'text' ? '#101918' : brushColor,
      fontSize: 24,
      fontFamily: "'Plus Jakarta Sans', sans-serif",
      fontWeight: 'bold',
      fontStyle: 'normal'
    };
    const updated = [...elements, newEl];
    setElements(updated);
    setActiveElementId(id);
    saveToHistory(updated, paths);

    // Focus the text element after a short delay to allow DOM to render
    if (type === 'text') {
      setTimeout(() => {
        const el = elementRefs.current[id];
        if (el) {
          const p = el.querySelector('div[contenteditable="true"]') as HTMLElement;
          p?.focus();
          // Select all text
          const range = document.createRange();
          range.selectNodeContents(p);
          const selection = window.getSelection();
          selection?.removeAllRanges();
          selection?.addRange(range);
        }
      }, 50);
    }
  };

  const deleteElement = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    const updated = elements.filter(el => el.id !== id);
    setElements(updated);
    setActiveElementId(null);
    saveToHistory(updated, paths);
  };

  const updateActiveElement = (updates: Partial<EditableElement>) => {
    if (!activeElementId) return;
    const updated = elements.map(el => el.id === activeElementId ? { ...el, ...updates } : el);
    setElements(updated);
  };

  const handlePointerDown = (e: React.PointerEvent, id?: string, cropMode?: any) => {
    dragStartPos.current = { x: e.clientX, y: e.clientY };

    // Handle crop mode
    if (activeTool === 'crop' && cropMode) {
      setCropDragMode(cropMode);
      return;
    }

    // Handle brush drawing
    if (activeTool === 'brush') {
      setIsDrawing(true);
      const rect = containerRef.current?.getBoundingClientRect();
      if (rect) {
        const x = (e.clientX - rect.left) / (zoom / 100);
        const y = (e.clientY - rect.top) / (zoom / 100);
        setPaths([...paths, `M ${x} ${y}`]);
      }
      return;
    }

    // Handle element dragging
    if (id) {
      // If clicking text and already active, don't trigger drag immediately if it's contentEditable
      const target = e.target as HTMLElement;
      if (target.getAttribute('contenteditable') === 'true') {
         setActiveElementId(id);
         return; 
      }
      setIsDragging(true);
      setActiveElementId(id);
      return;
    }

    // Click on canvas background
    if (activeTool === 'text') {
      const rect = canvasRef.current?.getBoundingClientRect();
      if (rect) {
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        addElementAt(x, y, 'text');
      }
    } else {
      setActiveElementId(null);
    }
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    const dx = e.clientX - dragStartPos.current.x;
    const dy = e.clientY - dragStartPos.current.y;
    const moveFactor = 0.2;

    if (activeTool === 'crop' && cropDragMode) {
      const newBox = { ...cropBox };
      if (cropDragMode === 'move') {
        newBox.x = Math.max(0, Math.min(100 - newBox.w, newBox.x + dx * moveFactor));
        newBox.y = Math.max(0, Math.min(100 - newBox.h, newBox.y + dy * moveFactor));
      } else if (cropDragMode === 'nw') {
        newBox.x = Math.max(0, Math.min(newBox.x + newBox.w - 5, newBox.x + dx * moveFactor));
        newBox.y = Math.max(0, Math.min(newBox.y + newBox.h - 5, newBox.y + dy * moveFactor));
        newBox.w = Math.max(5, newBox.w - (newBox.x - cropBox.x));
        newBox.h = Math.max(5, newBox.h - (newBox.y - cropBox.y));
      } else if (cropDragMode === 'se') {
        newBox.w = Math.max(5, Math.min(100 - newBox.x, newBox.w + dx * moveFactor));
        newBox.h = Math.max(5, Math.min(100 - newBox.y, newBox.h + dy * moveFactor));
      }
      setCropBox(newBox);
      dragStartPos.current = { x: e.clientX, y: e.clientY };
      return;
    }

    if (isDrawing && activeTool === 'brush') {
      const rect = containerRef.current?.getBoundingClientRect();
      if (rect) {
        const x = (e.clientX - rect.left) / (zoom / 100);
        const y = (e.clientY - rect.top) / (zoom / 100);
        const lastPath = paths[paths.length - 1];
        setPaths([...paths.slice(0, -1), `${lastPath} L ${x} ${y}`]);
      }
      return;
    }

    if (isDragging && activeElementId) {
      const rect = canvasRef.current?.getBoundingClientRect();
      if (rect) {
        setElements(elements.map(el => {
          if (el.id === activeElementId) {
            const dragDx = (dx / rect.width) * 100;
            const dragDy = (dy / rect.height) * 100;
            return { ...el, x: el.x + dragDx, y: el.y + dragDy };
          }
          return el;
        }));
        dragStartPos.current = { x: e.clientX, y: e.clientY };
      }
    }
  };

  const handlePointerUp = () => {
    if (isDrawing || isDragging) {
      saveToHistory(elements, paths);
    }
    setIsDragging(false);
    setIsDrawing(false);
    setCropDragMode(null);
  };

  return (
    <div className="fixed inset-0 z-[60] bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 md:p-6 animate-fade-in transition-all" onPointerUp={handlePointerUp}>
      <div className="bg-white dark:bg-[#1e293b] w-full max-w-[1400px] h-[92vh] rounded-2xl shadow-2xl overflow-hidden flex flex-col lg:flex-row border border-slate-200 dark:border-slate-800 relative ring-1 ring-black/5 transition-colors">
        
        {/* Left Workspace Area */}
        <div 
          className={`flex-1 relative group overflow-hidden flex items-center justify-center bg-[#f8fafc] dark:bg-slate-950 transition-all duration-500 ${activeTool ? 'lg:w-[calc(100%-350px)]' : 'w-full'} ${activeTool === 'text' ? 'cursor-text' : ''}`}
          onPointerMove={handlePointerMove}
        >
          <div className="absolute inset-0 opacity-30 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#cbd5e1 1.5px, transparent 1.5px)', backgroundSize: '24px 24px' }}></div>
          
          {/* Top Tool Selection Toolbar */}
          <div className="absolute top-6 left-1/2 -translate-x-1/2 z-[60] flex items-center gap-2 bg-white/90 dark:bg-slate-800/90 backdrop-blur shadow-xl border border-slate-100 dark:border-slate-700 rounded-full px-4 py-2 transition-all hover:shadow-2xl">
            {tools.map((tool) => (
              <button
                key={tool.id}
                onClick={() => setActiveTool(tool.id as ToolType)}
                className={`group p-3 rounded-full transition-all duration-200 flex items-center justify-center relative ${
                  activeTool === tool.id 
                  ? 'bg-primary text-slate-900 shadow-glow scale-110' 
                  : 'text-slate-400 hover:text-primary hover:bg-primary/5'
                }`}
                title={tool.label}
              >
                <span className="material-symbols-outlined text-[24px] group-hover:scale-105 transition-transform">
                  {tool.icon}
                </span>
              </button>
            ))}
            <div className="w-px h-8 bg-slate-200 dark:bg-slate-700 mx-1"></div>
            <button 
              onClick={onClose}
              className="p-3 rounded-full text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all"
            >
              <span className="material-symbols-outlined text-[24px]">close</span>
            </button>
          </div>

          {/* Canvas Wrapper */}
          <div className="relative z-10 p-10 lg:p-16 w-full h-full flex items-center justify-center pointer-events-auto" ref={containerRef}>
            <div 
              ref={canvasRef}
              className="relative shadow-2xl rounded-sm ring-1 ring-black/5 bg-white dark:bg-slate-800 p-0.5 group/image select-none overflow-hidden"
              onPointerDown={(e) => handlePointerDown(e)}
              style={{ transform: `scale(${zoom / 100})` }}
            >
              <img 
                alt="Editing Canvas" 
                className="max-w-full max-h-[65vh] object-contain rounded-sm pointer-events-none" 
                src={image?.url || image} 
                draggable={false}
              />
              
              {/* Overlay for brush paths */}
              <div className="absolute inset-0 z-20 pointer-events-none overflow-hidden">
                <svg className="w-full h-full overflow-visible">
                  {paths.map((p, i) => (
                    <path key={i} d={p} fill="none" stroke={brushColor} strokeWidth={brushSize} strokeLinecap="round" strokeLinejoin="round" />
                  ))}
                </svg>
              </div>

              {/* Editable Elements Layer */}
              <div className="absolute inset-0 z-30 pointer-events-none">
                {elements.map((el) => (
                  <div
                    key={el.id}
                    ref={(ref) => { elementRefs.current[el.id] = ref; }}
                    onPointerDown={(e) => { 
                      e.stopPropagation(); 
                      handlePointerDown(e, el.id);
                    }}
                    className={`absolute pointer-events-auto flex items-center justify-center p-2 border-2 ${activeElementId === el.id ? 'border-primary shadow-[0_0_10px_rgba(129,216,208,0.5)] bg-primary/5' : 'border-transparent'} hover:border-primary/50 transition-all cursor-move`}
                    style={{ left: `${el.x}%`, top: `${el.y}%`, transform: 'translate(-50%, -50%)' }}
                  >
                    {/* Delete button (only when active) */}
                    {activeElementId === el.id && (
                      <button 
                        onPointerDown={(e) => e.stopPropagation()}
                        onClick={(e) => deleteElement(e, el.id)}
                        className="absolute -top-3 -right-3 size-6 bg-red-500 text-white rounded-full flex items-center justify-center shadow-lg hover:bg-red-600 transition-colors z-50 pointer-events-auto"
                      >
                        <span className="material-symbols-outlined text-sm font-bold">close</span>
                      </button>
                    )}

                    {el.type === 'text' ? (
                      <div 
                        contentEditable
                        suppressContentEditableWarning
                        onBlur={(e) => {
                          const newText = e.currentTarget.textContent || '';
                          updateActiveElement({ content: newText });
                          saveToHistory(elements.map(item => item.id === el.id ? { ...item, content: newText } : item), paths);
                        }}
                        className="whitespace-nowrap px-2 py-1 outline-none min-w-[50px] text-center transition-all bg-transparent"
                        style={{ 
                          color: el.color, 
                          fontSize: `${el.fontSize}px`, 
                          fontFamily: el.fontFamily,
                          fontWeight: el.fontWeight, 
                          fontStyle: el.fontStyle,
                          cursor: 'text'
                        }}
                      >
                        {el.content}
                      </div>
                    ) : (
                      <span className="material-symbols-outlined select-none" style={{ color: el.color, fontSize: '64px' }}>
                        {shapesList.find(s => s.type === el.shapeType)?.icon || 'star'}
                      </span>
                    )}
                  </div>
                ))}
              </div>

              {/* Crop Box UI */}
              {activeTool === 'crop' && (
                <div className="absolute inset-0 z-40 bg-black/50 pointer-events-auto">
                   <div 
                     onPointerDown={(e) => handlePointerDown(e, undefined, 'move')}
                     className="absolute border-2 border-white shadow-[0_0_0_9999px_rgba(0,0,0,0.4)] cursor-move transition-all"
                     style={{ left: `${cropBox.x}%`, top: `${cropBox.y}%`, width: `${cropBox.w}%`, height: `${cropBox.h}%` }}
                   >
                      <div className="absolute inset-0 grid grid-cols-3 grid-rows-3 opacity-30 pointer-events-none">
                        {[...Array(8)].map((_, i) => <div key={i} className="border-[0.5px] border-white/50"></div>)}
                      </div>
                      <div onPointerDown={(e) => { e.stopPropagation(); handlePointerDown(e, undefined, 'nw'); }} className="absolute -top-2 -left-2 size-4 bg-white border border-primary rounded-sm cursor-nw-resize shadow-md"></div>
                      <div onPointerDown={(e) => { e.stopPropagation(); handlePointerDown(e, undefined, 'se'); }} className="absolute -bottom-2 -right-2 size-4 bg-white border border-primary rounded-sm cursor-se-resize shadow-md"></div>
                   </div>
                </div>
              )}
            </div>
          </div>

          {/* Bottom Zoom & History Control Bar */}
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-3 bg-white/95 dark:bg-slate-800/95 backdrop-blur-md border border-slate-200/60 dark:border-slate-700 rounded-full px-5 py-2 shadow-soft text-slate-500 z-20">
            <button onClick={() => setZoom(Math.max(25, zoom - 10))} className="hover:text-primary transition-colors p-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700">
              <span className="material-symbols-outlined text-[20px]">remove</span>
            </button>
            <span className="text-xs font-bold text-slate-600 dark:text-slate-300 w-12 text-center font-mono">{zoom}%</span>
            <button onClick={() => setZoom(Math.min(300, zoom + 10))} className="hover:text-primary transition-colors p-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700">
              <span className="material-symbols-outlined text-[20px]">add</span>
            </button>
            <div className="w-px h-5 bg-slate-200 dark:bg-slate-700 mx-1"></div>
            <button onClick={handleUndo} disabled={historyIndex < 0} className={`p-1.5 rounded-full ${historyIndex >= 0 ? 'hover:text-primary hover:bg-slate-100 dark:hover:bg-slate-700' : 'opacity-30'}`}><span className="material-symbols-outlined text-[20px]">undo</span></button>
            <button onClick={handleRedo} disabled={historyIndex >= history.length - 1} className={`p-1.5 rounded-full ${historyIndex < history.length - 1 ? 'hover:text-primary hover:bg-slate-100 dark:hover:bg-slate-700' : 'opacity-30'}`}><span className="material-symbols-outlined text-[20px]">redo</span></button>
          </div>
        </div>

        {/* Right Properties Panel */}
        {activeTool && (
          <div className="w-full lg:w-[350px] flex flex-col bg-white dark:bg-[#1e293b] border-t lg:border-t-0 lg:border-l border-slate-100 dark:border-slate-800 relative z-20 shadow-xl animate-slide-in-right transition-colors">
            <div className="flex items-center justify-between p-6 border-b border-slate-50 dark:border-slate-800 shrink-0 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm sticky top-0 z-10">
              <div>
                <h2 className="text-slate-900 dark:text-white text-lg font-bold tracking-tight">属性设置</h2>
                <div className="flex items-center gap-1.5 mt-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
                  <p className="text-slate-500 dark:text-slate-400 text-[10px] uppercase tracking-widest font-black">
                    {tools.find(t => t.id === activeTool)?.label} 激活中
                  </p>
                </div>
              </div>
              <button onClick={() => setActiveTool(null)} className="text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors rounded-full p-2 hover:bg-slate-50 dark:hover:bg-slate-800"><span className="material-symbols-outlined text-[20px]">close</span></button>
            </div>

            <div className="flex-1 overflow-y-auto sidebar-scroll p-6 space-y-8">
              {/* Tool Specific Settings */}
              {activeTool === 'text' && (
                <div className="space-y-6">
                   {activeElement?.type === 'text' ? (
                     <div className="space-y-6">
                        {/* Font Family Selection */}
                        <div>
                          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 block">字体族</label>
                          <div className="grid grid-cols-1 gap-2">
                            {fontFamilies.map((font) => (
                              <button
                                key={font.name}
                                onClick={() => updateActiveElement({ fontFamily: font.value })}
                                className={`flex items-center px-4 py-3 rounded-xl border text-sm transition-all text-left ${
                                  activeElement.fontFamily === font.value 
                                  ? 'bg-primary/10 border-primary text-primary-dark font-black' 
                                  : 'bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-primary/50'
                                }`}
                                style={{ fontFamily: font.value }}
                              >
                                {font.name}
                              </button>
                            ))}
                          </div>
                        </div>

                        {/* Font Size Slider */}
                        <div>
                          <div className="flex justify-between items-center mb-2">
                            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">字体大小</label>
                            <span className="text-[11px] font-bold text-primary">{activeElement.fontSize}px</span>
                          </div>
                          <input 
                            type="range" min="12" max="120"
                            value={activeElement.fontSize}
                            onChange={(e) => updateActiveElement({ fontSize: parseInt(e.target.value) })}
                            className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-primary"
                          />
                        </div>

                        {/* Weight and Style Toggles */}
                        <div className="flex gap-2">
                          <button 
                            onClick={() => updateActiveElement({ fontWeight: activeElement.fontWeight === 'bold' ? 'normal' : 'bold' })}
                            className={`flex-1 py-3 rounded-xl text-xs font-black transition-all ${activeElement.fontWeight === 'bold' ? 'bg-primary text-slate-900 shadow-md' : 'bg-slate-50 dark:bg-slate-800 text-slate-500 border border-slate-100 dark:border-slate-700'}`}
                          >粗体 (B)</button>
                          <button 
                            onClick={() => updateActiveElement({ fontStyle: activeElement.fontStyle === 'italic' ? 'normal' : 'italic' })}
                            className={`flex-1 py-3 rounded-xl text-xs font-black italic transition-all ${activeElement.fontStyle === 'italic' ? 'bg-primary text-slate-900 shadow-md' : 'bg-slate-50 dark:bg-slate-800 text-slate-500 border border-slate-100 dark:border-slate-700'}`}
                          >斜体 (I)</button>
                        </div>

                        {/* Text Color Picker */}
                        <div>
                          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 block">文字颜色</label>
                          <div className="grid grid-cols-6 gap-2">
                            {['#000000', '#FFFFFF', '#FF0000', '#00FF00', '#0000FF', '#81D8D0', '#FFD700', '#FF69B4'].map(c => (
                              <button 
                                key={c}
                                onClick={() => updateActiveElement({ color: c })}
                                className={`size-8 rounded-full border shadow-sm transition-all ${activeElement.color === c ? 'ring-2 ring-primary ring-offset-2 scale-110' : 'border-slate-200 dark:border-slate-700 hover:scale-105'}`}
                                style={{ backgroundColor: c }}
                              />
                            ))}
                          </div>
                        </div>
                     </div>
                   ) : (
                     <div className="py-10 text-center bg-slate-50 dark:bg-slate-800/30 rounded-2xl border border-dashed border-slate-200 dark:border-slate-700">
                        <span className="material-symbols-outlined text-4xl text-slate-300 mb-3">mouse</span>
                        <p className="text-xs text-slate-400 px-6 font-medium leading-relaxed">在画布任意位置点击开始输入文字。支持直接点击文字进行拖拽。</p>
                     </div>
                   )}
                </div>
              )}

              {activeTool === 'brush' && (
                <div className="space-y-6">
                  <div>
                    <div className="flex justify-between items-center mb-4">
                      <label className="text-xs font-black text-slate-400 uppercase tracking-widest">笔触大小</label>
                      <span className="text-xs font-mono font-bold text-primary bg-primary/10 px-2 py-0.5 rounded">{brushSize}px</span>
                    </div>
                    <input 
                      type="range" min="1" max="50"
                      value={brushSize}
                      onChange={(e) => setBrushSize(parseInt(e.target.value))}
                      className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-primary" 
                    />
                  </div>
                  <div>
                    <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">笔触颜色</h3>
                    <div className="grid grid-cols-6 gap-3">
                      {['#81D8D0', '#000000', '#FFFFFF', '#FF6B6B', '#4ECDC4', '#FFE66D'].map(color => (
                        <button 
                          key={color} 
                          onClick={() => setBrushColor(color)}
                          className={`w-8 h-8 rounded-full border shadow-sm transition-all ${brushColor === color ? 'ring-2 ring-primary ring-offset-2 scale-110' : 'border-slate-200 dark:border-slate-700'}`}
                          style={{ backgroundColor: color }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTool === 'shapes' && (
                <div className="space-y-6">
                  <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">选择形状</h3>
                  <div className="grid grid-cols-4 gap-4">
                    {shapesList.map((shape) => (
                      <button 
                        key={shape.type}
                        onClick={() => addElementAt(50, 50, 'shape', shape.type)}
                        className="aspect-square rounded-xl border border-slate-100 dark:border-slate-700 flex items-center justify-center hover:bg-primary/10 hover:border-primary transition-all group bg-slate-50 dark:bg-slate-800/30"
                      >
                        <span className="material-symbols-outlined text-slate-500 group-hover:text-primary transition-colors text-[28px]">{shape.icon}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {activeTool === 'crop' && (
                <div className="space-y-6">
                   <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-medium">拖动白色手柄调整裁剪大小，拖动中心区域移动裁剪框。</p>
                </div>
              )}
            </div>

            {/* Bottom Actions for Save/Cancel */}
            <div className="p-6 border-t border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shrink-0 space-y-3 shadow-[0_-10px_40px_rgba(0,0,0,0.02)]">
              <button 
                onClick={() => onSave(image?.url || image)}
                className="w-full bg-primary hover:bg-[#68cdc4] active:scale-95 text-slate-900 font-black text-sm py-4 rounded-xl flex items-center justify-center gap-2 transition-all shadow-xl shadow-primary/20"
              >
                <span className="material-symbols-outlined text-[20px] font-bold">check_circle</span>
                确认并保存
              </button>
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes slide-in-right {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        .animate-slide-in-right {
          animation: slide-in-right 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .shadow-soft {
          box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.1);
        }
        input[type=range]::-webkit-slider-thumb {
          -webkit-appearance: none;
          height: 16px;
          width: 16px;
          border-radius: 50%;
          background: #81D8D0;
          cursor: pointer;
          border: 2px solid white;
          box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        div[contenteditable="true"]:focus {
          outline: none;
        }
      `}</style>
    </div>
  );
};

export default ImageEditor;
