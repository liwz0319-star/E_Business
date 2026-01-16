
import React, { useState } from 'react';

interface AssetsProps {
  onGenerate: () => void;
  onAssetClick?: (asset: any) => void;
}

type AssetType = 'all' | 'image' | 'video' | 'copy';
type ViewMode = 'module' | 'list';

const Assets: React.FC<AssetsProps> = ({ onGenerate, onAssetClick }) => {
  const [activeCategory, setActiveCategory] = useState<AssetType>('all');
  const [viewMode, setViewMode] = useState<ViewMode>('module');
  const [selectedIds, setSelectedIds] = useState<number[]>([1, 2]);

  const allAssets = [
    { id: 1, title: 'Summer Sneaker V1', time: '2m ago', type: 'image', icon: 'image', color: 'text-primary', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBgOlJf4NzO9iBCkgZHbLH-DVQg4KyST1yl6985A6YVEL-623eToI5BA16FqQe3o4vRARMOfCjLPsiAnfFs3UEL5n3c9T1gJRkpehjjSW33BLmKtEVBOhyvPlpY0kcceWaJlOO6Pmtks5Yd3tpuj3HJLyEgBADq5JWfL4wqOqtXnASesRo7eAVrkLGokAmU2evWlUrM9c6gm52ZuxcWn6zQ0QF7z6L8Pw1aXENo-uVHFCrD76v89QjM9SiydetlQ8nRVx7_8Vm9v68' },
    { id: 2, title: 'TikTok Demo Reel', time: '1h ago', type: 'video', icon: 'videocam', color: 'text-purple-400', duration: '0:15', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBvQo5U6aOgbcNz09dJbCJKp-YXHf-j-1TUws2yWWkJ23oDD_S4LIek05ChviWp8tNZc1uGA7w0r4biJWtoCPNFKVok3UvTuov6sPzN_ua0ugovTp3WVuTcNC1Jz3orsSxCaXC6ttlBmhjl4fKslqeNe04ae8qsHVTENPtg4hFGkibxB8M-n9vIRIlwQmDVr-ck0i8GoC9nkpK4FWcctsxKmpoONJOv-5LSMB0jbZT6jHIZkqEKOaiL9-wpE-pPKhlQ3UrrOda_3eg' },
    { id: 3, title: 'IG Captions - Spring', time: '1d ago', type: 'copy', icon: 'description', color: 'text-orange-400' },
    { id: 4, title: 'Vitamin C Serum', time: '2d ago', type: 'image', icon: 'image', color: 'text-primary', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBdwcHszBsPslbVpSztJchtv1OzXAPaie9X5hnaSy7dhwBVndmNx0Vi9LSkHdU6Y8jrXzYS_IgKZUqgW2M817CMvk_UF89thNti1dOJd4vGoCDy_wpw-SjX6C3FcHf4I6fSFTwQ3YgQuj4FwYSHdwRT7CAaszgEI9nlrvV3cDMVAVEVUsgjQwDA3bPZPYc4khp0IDr0Y1UjQy6sozo3KIVlITgBmPIxgP91nPmrzcKaGvt8BaUivEy7oZ774xJB4e85GlRWl1FtwNA' },
    { id: 5, title: 'Website Hero Banner', time: '3d ago', type: 'image', icon: 'image', color: 'text-primary', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDWeYdIhlHuSQ6XW1TZ6NXpkedYXTluj9wzSBIiSlfTKzTZWFkuSLctRopeZN8Tg-VMl76gGdYTFEzkGsTvA_NfywpMVN7xLOTYjRohSO1B_RBUFOgIYuCsdLzYqS68bV5Tafl6aaXsSCMMUgXBpxXBUXktpXJ-DmxcCW_XsPVFHptiW3qgBkkb2fnbQxxf538hPw8EdfGKmQxzNuWiAWXHCasHZCJ8h2zq4FMRZ5-_SVi4lxGIw2Emebc0-iA8-3pyxb1k6h6RYik' },
    { id: 6, title: 'Product Unboxing', time: '4d ago', type: 'video', icon: 'videocam', color: 'text-purple-400', duration: '1:20', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDWeYdIhlHuSQ6XW1TZ6NXpkedYXTluj9wzSBIiSlfTKzTZWFkuSLctRopeZN8Tg-VMl76gGdYTFEzkGsTvA_NfywpMVN7xLOTYjRohSO1B_RBUFOgIYuCsdLzYqS68bV5Tafl6aaXsSCMMUgXBpxXBUXktpXJ-DmxcCW_XsPVFHptiW3qgBkkb2fnbQxxf538hPw8EdfGKmQxzNuWiAWXHCasHZCJ8h2zq4FMRZ5-_SVi4lxGIw2Emebc0-iA8-3pyxb1k6h6RYik' },
    { id: 7, title: 'Email Sequence - Welcome', time: '5d ago', type: 'copy', icon: 'description', color: 'text-orange-400' },
    { id: 8, title: 'Leather Handbag 02', time: '1w ago', type: 'image', icon: 'image', color: 'text-primary', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDvuSuvgLtmem_fUPFDgrCLpLO3FuEYCcebtYVeqM5AmL3j7wJUE0rXIfPZt_LsGs3Klbbq72p4hm8fnNoqukST2hKLAFpe92OrdZwkedG7Xbd9WW-IAHPE__H5_G9tENKSDoZMUCHlvPVSs-Mq3Pv0thH9C4YaPGyR_9OAUQsL5GuTWbe57JYnFmYGYkcayZb4jmQi_cfysfdd6AhW9iwIvK9Fgf3SeAa8PTnUCg0XTr92hyQ6rK98gwNQZ65EwCiEiPZUGIwqoAs' }
  ];

  const filteredAssets = allAssets.filter(asset => activeCategory === 'all' || asset.type === activeCategory);

  const toggleSelection = (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  const handleBulkAction = (action: string) => {
    alert(`${action} performed on ${selectedIds.length} assets.`);
    if (action === 'delete') setSelectedIds([]);
  };

  const handleUpload = () => {
    alert("Opening file selector...");
  };

  const handleMoreOptions = (e: React.MouseEvent, title: string) => {
    e.stopPropagation();
    alert(`Options for ${title}`);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-background-light dark:bg-background-dark font-inter transition-colors">
      <header className="bg-surface-light dark:bg-surface-dark border-b border-[#e9f1f0] dark:border-[#2d3b3a] px-8 py-6 shrink-0 z-10 transition-colors">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 max-w-7xl mx-auto w-full">
          <div className="flex flex-col gap-1">
            <h2 className="text-2xl font-black tracking-tight text-[#101918] dark:text-white">Assets Library</h2>
            <p className="text-[#5b8b86] text-sm">Manage your AI-generated and uploaded marketing assets.</p>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={handleUpload}
              className="flex items-center justify-center h-10 px-4 bg-white dark:bg-[#2d3b3a] text-[#101918] dark:text-white border border-[#e9f1f0] dark:border-[#2d3b3a] rounded-lg text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow-sm"
            >
              <span className="material-symbols-outlined text-lg mr-2">cloud_upload</span>
              Upload New
            </button>
            <button 
              onClick={onGenerate}
              className="flex items-center justify-center gap-2 h-10 px-4 bg-primary hover:bg-secondary text-[#101918] rounded-lg transition-all text-sm font-bold shadow-sm shadow-primary/20"
            >
              <span className="material-symbols-outlined text-lg">add</span>
              <span>Generate</span>
            </button>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto sidebar-scroll p-8">
        <div className="max-w-7xl mx-auto flex flex-col gap-6 pb-24">
          {/* Filters & Search */}
          <div className="flex flex-col lg:flex-row gap-4 items-center justify-between sticky top-0 z-10 -mx-8 px-8 py-4 bg-background-light/95 dark:bg-background-dark/95 backdrop-blur-sm border-b border-transparent transition-colors">
            <div className="relative w-full lg:max-w-md group">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[#5b8b86] material-symbols-outlined">search</span>
              <input 
                className="w-full h-11 pl-10 pr-4 bg-white dark:bg-[#1e2928] border-none rounded-xl shadow-sm ring-1 ring-[#e9f1f0] dark:ring-[#2d3b3a] focus:ring-2 focus:ring-primary text-sm placeholder:text-[#9ca3af] dark:text-white transition-all" 
                placeholder="Search by name, type, or date..." 
                type="text"
              />
            </div>
            <div className="flex items-center gap-2 w-full lg:w-auto overflow-x-auto pb-1 lg:pb-0 no-scrollbar">
              <button 
                onClick={() => setActiveCategory('all')}
                className={`shrink-0 h-9 px-4 rounded-lg text-sm font-semibold transition-all ${activeCategory === 'all' ? 'bg-primary text-[#101918] shadow-sm' : 'bg-white dark:bg-[#1e2928] text-[#5b8b86]'}`}
              >
                All Assets
              </button>
              <button 
                onClick={() => setActiveCategory('image')}
                className={`shrink-0 h-9 px-4 rounded-lg text-sm font-medium transition-all border ${activeCategory === 'image' ? 'bg-primary text-[#101918] border-transparent' : 'bg-white dark:bg-[#1e2928] text-[#5b8b86] border-[#e9f1f0] dark:border-[#2d3b3a]'}`}
              >
                Images
              </button>
              <button 
                onClick={() => setActiveCategory('video')}
                className={`shrink-0 h-9 px-4 rounded-lg text-sm font-medium transition-all border ${activeCategory === 'video' ? 'bg-primary text-[#101918] border-transparent' : 'bg-white dark:bg-[#1e2928] text-[#5b8b86] border-[#e9f1f0] dark:border-[#2d3b3a]'}`}
              >
                Videos
              </button>
              <button 
                onClick={() => setActiveCategory('copy')}
                className={`shrink-0 h-9 px-4 rounded-lg text-sm font-medium transition-all border ${activeCategory === 'copy' ? 'bg-primary text-[#101918] border-transparent' : 'bg-white dark:bg-[#1e2928] text-[#5b8b86] border-[#e9f1f0] dark:border-[#2d3b3a]'}`}
              >
                Copy
              </button>
              <div className="h-6 w-px bg-gray-200 dark:bg-gray-700 mx-2"></div>
              <button 
                onClick={() => setViewMode('module')}
                className={`shrink-0 h-9 w-9 flex items-center justify-center rounded-lg transition-all border ${viewMode === 'module' ? 'bg-primary text-[#101918] border-transparent' : 'bg-white dark:bg-[#1e2928] text-[#5b8b86] border-[#e9f1f0] dark:border-[#2d3b3a]'}`}
              >
                <span className="material-symbols-outlined text-[20px]">view_module</span>
              </button>
              <button 
                onClick={() => setViewMode('list')}
                className={`shrink-0 h-9 w-9 flex items-center justify-center rounded-lg transition-all ${viewMode === 'list' ? 'bg-primary text-[#101918]' : 'text-[#5b8b86] hover:bg-white dark:hover:bg-[#1e2928]'}`}
              >
                <span className="material-symbols-outlined text-[20px]">view_list</span>
              </button>
            </div>
          </div>

          {/* Asset Grid / List */}
          {viewMode === 'module' ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {filteredAssets.map((asset) => (
                <div 
                  key={asset.id} 
                  onClick={() => onAssetClick?.(asset)}
                  className={`group relative flex flex-col gap-3 rounded-xl bg-white dark:bg-[#1e2928] p-3 shadow-sm hover:shadow-lg transition-all duration-300 ring-1 ring-black/5 dark:ring-white/5 cursor-pointer ${selectedIds.includes(asset.id) ? 'ring-2 ring-primary bg-primary/5' : ''}`}
                >
                  <div className={`absolute top-3 left-3 z-20 transition-opacity ${selectedIds.includes(asset.id) ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}>
                    <input 
                      readOnly
                      checked={selectedIds.includes(asset.id)}
                      onClick={(e) => toggleSelection(e, asset.id)}
                      className="h-5 w-5 rounded border-gray-300 text-primary focus:ring-primary cursor-pointer shadow-sm" 
                      type="checkbox"
                    />
                  </div>
                  <div className="absolute top-3 right-3 z-20 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button 
                      onClick={(e) => handleMoreOptions(e, asset.title)}
                      className="h-8 w-8 rounded-full bg-white/90 dark:bg-black/60 backdrop-blur-sm shadow-sm flex items-center justify-center hover:bg-white text-gray-700 dark:text-white"
                    >
                      <span className="material-symbols-outlined text-lg">more_horiz</span>
                    </button>
                  </div>
                  
                  <div className="relative w-full aspect-[4/3] rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800">
                    {asset.type === 'copy' ? (
                      <div className="w-full h-full bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 border border-dashed border-gray-200 dark:border-gray-700 p-4 flex flex-col gap-2 select-none">
                        <div className="h-2 w-1/3 bg-gray-200 dark:bg-gray-600 rounded"></div>
                        <div className="h-2 w-full bg-gray-200 dark:bg-gray-600 rounded"></div>
                        <div className="h-2 w-5/6 bg-gray-200 dark:bg-gray-600 rounded"></div>
                        <div className="h-2 w-full bg-gray-200 dark:bg-gray-600 rounded"></div>
                        <div className="mt-auto self-end">
                          <span className={`material-symbols-outlined text-3xl opacity-30 ${asset.color}`}>
                            {asset.icon === 'description' && asset.title.includes('Email') ? 'mail' : asset.icon}
                          </span>
                        </div>
                      </div>
                    ) : (
                      <div className={`w-full h-full bg-cover bg-center transition-transform duration-500 group-hover:scale-105 ${asset.type === 'video' ? 'opacity-90' : ''}`} style={{ backgroundImage: `url('${asset.img}')` }}>
                        {asset.type === 'video' && (
                          <div className="absolute inset-0 flex items-center justify-center">
                            <span className="material-symbols-outlined text-4xl text-white drop-shadow-lg opacity-80 group-hover:opacity-100 group-hover:scale-110 transition-all">play_circle</span>
                          </div>
                        )}
                        {asset.duration && (
                          <div className="absolute bottom-2 right-2 bg-black/60 px-1.5 py-0.5 rounded text-[10px] text-white font-medium backdrop-blur-sm">
                            {asset.duration}
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="px-1">
                    <h3 className="text-sm font-semibold text-[#101918] dark:text-white truncate" title={asset.title}>{asset.title}</h3>
                    <div className="flex items-center gap-1.5 mt-1">
                      <span className={`material-symbols-outlined text-[14px] ${asset.color}`}>
                        {asset.type === 'video' ? 'videocam' : asset.icon}
                      </span>
                      <p className="text-[#5b8b86] text-xs font-normal">{asset.time}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white dark:bg-[#1e2928] rounded-xl overflow-hidden shadow-sm border border-[#e9f1f0] dark:border-[#2d3b3a]">
              <table className="w-full text-left">
                <thead className="bg-gray-50 dark:bg-[#2d3b3a]/30 border-b border-[#e9f1f0] dark:border-[#2d3b3a]">
                  <tr>
                    <th className="px-6 py-4 w-12"><input type="checkbox" className="rounded border-gray-300 text-primary" onChange={(e) => setSelectedIds(e.target.checked ? allAssets.map(a => a.id) : [])} /></th>
                    <th className="px-6 py-4 text-xs font-bold text-[#5b8b86] uppercase tracking-wider">Asset Name</th>
                    <th className="px-6 py-4 text-xs font-bold text-[#5b8b86] uppercase tracking-wider">Type</th>
                    <th className="px-6 py-4 text-xs font-bold text-[#5b8b86] uppercase tracking-wider">Created</th>
                    <th className="px-6 py-4 text-xs font-bold text-[#5b8b86] uppercase tracking-wider text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#e9f1f0] dark:divide-[#2d3b3a]">
                  {filteredAssets.map(asset => (
                    <tr 
                      key={asset.id} 
                      onClick={() => onAssetClick?.(asset)}
                      className={`hover:bg-gray-50 dark:hover:bg-white/5 transition-colors cursor-pointer ${selectedIds.includes(asset.id) ? 'bg-primary/5' : ''}`}
                    >
                      <td className="px-6 py-4"><input readOnly checked={selectedIds.includes(asset.id)} onClick={(e) => toggleSelection(e, asset.id)} type="checkbox" className="rounded border-gray-300 text-primary" /></td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          {asset.img ? (
                            <img src={asset.img} className="h-10 w-10 rounded object-cover border border-gray-200" />
                          ) : (
                            <div className="h-10 w-10 rounded bg-gray-100 flex items-center justify-center"><span className={`material-symbols-outlined ${asset.color}`}>{asset.icon}</span></div>
                          )}
                          <span className="font-semibold text-sm">{asset.title}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4"><span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded capitalize">{asset.type}</span></td>
                      <td className="px-6 py-4 text-sm text-[#5b8b86]">{asset.time}</td>
                      <td className="px-6 py-4 text-right">
                        <button onClick={(e) => handleMoreOptions(e, asset.title)} className="p-1 hover:bg-gray-100 dark:hover:bg-white/10 rounded"><span className="material-symbols-outlined text-gray-400">more_vert</span></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Floating Action Bar */}
      {selectedIds.length > 0 && (
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-30 animate-fade-in-up">
          <div className="flex items-center gap-1 p-1.5 bg-slate-900 dark:bg-white rounded-2xl shadow-xl shadow-black/20 ring-1 ring-white/10 text-white dark:text-slate-900 transition-colors">
            <div className="px-3 text-sm font-medium border-r border-slate-700 dark:border-slate-200 pr-3">
              {selectedIds.length} Selected
            </div>
            <button 
              onClick={() => handleBulkAction('Downloading')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl hover:bg-white/10 dark:hover:bg-black/5 transition-colors text-xs font-medium"
            >
              <span className="material-symbols-outlined text-lg">download</span>
              Download
            </button>
            <button 
              onClick={() => handleBulkAction('Archiving')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl hover:bg-white/10 dark:hover:bg-black/5 transition-colors text-xs font-medium"
            >
              <span className="material-symbols-outlined text-lg">archive</span>
              Archive
            </button>
            <button 
              onClick={() => handleBulkAction('delete')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl hover:bg-red-500/20 text-red-400 dark:text-red-600 transition-colors text-xs font-medium"
            >
              <span className="material-symbols-outlined text-lg">delete</span>
              Delete
            </button>
            <button 
              onClick={() => setSelectedIds([])}
              className="ml-1 p-1 rounded-full hover:bg-white/10 dark:hover:bg-black/5"
            >
              <span className="material-symbols-outlined text-lg">close</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Assets;
