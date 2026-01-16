
import React, { useState, useMemo } from 'react';

interface GalleryProps {
  onGenerateNew: () => void;
  onAssetClick?: (asset: any) => void;
}

type Category = 'All' | 'Product Images' | 'Ad Videos' | 'Marketing Copy';

const Gallery: React.FC<GalleryProps> = ({ onGenerateNew, onAssetClick }) => {
  const [activeTab, setActiveTab] = useState<Category>('All');
  const [searchQuery, setSearchQuery] = useState('');

  const items = useMemo(() => [
    { 
      id: 1, 
      title: 'Flora Essence No.5', 
      type: 'Product Images', 
      tag: 'IMG', 
      meta: 'High-res Render • 4K', 
      url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCusrk-fGSMOjIPLv34G4cc0vDlzaFYmWwsg4ur48BogIpoXFLvKoblZ-EGLU_qiqf7IhX6PFzvCx55tbvl3qmuNZ7ugm5o6zszwhgYwJpT15udjk6sAdmE-ga2u3vx_4aclx42x02-AlUvt9pGOjmyLGnmqD78qd_-so56dKurxqwdusPsRyvi6BuxQJPhtlPBjaL7I0T8rtaAvWF6uxQRuSzJkgWmYYQecC17Xg5U51TMaSr4KTXVUJ0zs2fKIwn34XS96gZ0t4M',
      isVertical: false
    },
    { 
      id: 2, 
      title: 'Instagram Caption', 
      type: 'Marketing Copy', 
      tag: 'COPY', 
      meta: 'Generated 2h ago', 
      content: '"Step into the season with confidence. Our latest collection blends timeless elegance with modern comfort. #FallFashion #NewArrivals"',
      isText: true
    },
    { 
      id: 3, 
      title: 'Fall Teaser Story', 
      type: 'Ad Videos', 
      tag: 'VIDEO', 
      meta: '9:16 Vertical • Social Media', 
      url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAE69hLxboFK2IhbRA-JLBTNS4F6VSOXb73rePRq_BsVLcL34NICkkphV4WGOnif3yrXkny2bM16UIzJTG9FUDbw59C6-gziKSEK9GGD-2tS4G3yS0TxfCjW_GKwQWV30LMohdrmd9S9rV4W5aUNUWuuAg2TOwybNi7x8lw7xdRoekhWeEFTkFQLkPE2cr8gM3wE-HbOmDjrcfAyvOHdz65J4-VT-xdRAhMq-sxvLMcwqH3EIEr5-qbNNmQIR9xKntfAf5-pMjoE4A',
      isVertical: true,
      duration: '0:15'
    },
    { 
      id: 4, 
      title: 'Air Runner V2', 
      type: 'Product Images', 
      tag: 'IMG', 
      meta: 'Product Shot • Transparent BG', 
      url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuC0WwhjGemC4Prst4wgDp3eOshTSGfcR--zRts79ROF8jMDjEUqNbfaOhDDfBg6XOON1ryswveIMrL5USShF4Cqd_NXeSA8VIWnV8FinlatB3YefTbb0Pbo9K0dqRhtO7dcnUBp6NHKm83tN6fl6NHF3jqjewqMRk1z_rRnyPEG144583xUAyxwaXzmmkOMKhoRgboaRqjVnqQTWOBIYCQvkXIiFM1LFr1zJzyP8dDLSEOjFTscaYPKzePrBZPwLqWj1Y-3luuyBzM',
      isVertical: false
    },
    { 
      id: 5, 
      title: 'Subject: The wait is over...', 
      type: 'Marketing Copy', 
      tag: 'EMAIL', 
      meta: 'Generated 1d ago', 
      content: '"Hey [Name], The wait is finally over. We\'ve just restocked our best-selling items, but they won\'t last long. Grab your favorites before they\'re gone again."',
      isText: true
    },
    { 
      id: 6, 
      title: 'Midnight Chrono', 
      type: 'Product Images', 
      tag: 'IMG', 
      meta: 'Lifestyle Shot • Dark Theme', 
      url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCMQ2_XwFh8EOeVr1hxSenkcH845dfi-Lspcu-o33hkatw7Dix5nbpg2M0v6wRLCAZwAqEKvnJSjG54dJokM0ZL8vEZzjqNkmv6IPbVDc-h59OtJxTI2G8fwVTmYXh3nweNIHvSbNHDxEKHzsNS4vt_rW8zfomCL0qW4L2_J0yxSbpsG5FVC7tiyIv68oggVPZQzDP_XF-lJwW6QmYNLibCJI5lQRIL8mrM9_4t9PkDIJc4OZefIOiYPdKP2vDJ1CS3jERrtfgTi30',
      isVertical: false
    }
  ], []);

  const filteredItems = useMemo(() => {
    return items.filter(item => {
      const matchesTab = activeTab === 'All' || item.type === activeTab;
      const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesTab && matchesSearch;
    });
  }, [activeTab, searchQuery, items]);

  const handleAction = (action: string, title: string) => {
    alert(`${action} performed on: ${title}`);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-background-light dark:bg-background-dark font-inter overflow-hidden">
      <header className="bg-background-light/80 dark:bg-background-dark/95 backdrop-blur-md z-30 sticky top-0 shrink-0 border-b border-border-light/50 dark:border-border-dark/50 transition-colors">
        <div className="px-8 pt-8 pb-4">
          <div className="flex flex-wrap justify-between items-end gap-4 max-w-[1400px] mx-auto w-full">
            <div className="flex flex-col gap-1">
              <h2 className="text-[#0f1a19] dark:text-white text-3xl font-black tracking-tight">Creative Portfolio</h2>
              <p className="text-[#568f8c] text-base">Manage and curate your AI-generated assets.</p>
            </div>
            <button 
              onClick={onGenerateNew}
              className="flex items-center gap-2 bg-primary hover:bg-[#5ccbc4] text-[#0f1a19] px-5 py-2.5 rounded-xl font-bold text-sm transition-all shadow-sm hover:shadow-md transform hover:-translate-y-0.5 active:scale-95"
            >
              <span className="material-symbols-outlined text-xl">add</span>
              <span>Generate New</span>
            </button>
          </div>
        </div>
        <div className="px-8 pb-4">
          <div className="max-w-[1400px] mx-auto flex flex-col md:flex-row gap-4 justify-between items-center w-full">
            <div className="flex gap-2 overflow-x-auto no-scrollbar w-full md:w-auto pb-1 md:pb-0">
              {(['All', 'Product Images', 'Ad Videos', 'Marketing Copy'] as Category[]).map((cat) => (
                <button 
                  key={cat}
                  onClick={() => setActiveTab(cat)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all active:scale-95 whitespace-nowrap ${
                    activeTab === cat 
                    ? 'bg-[#0f1a19] text-white shadow-sm' 
                    : 'bg-white dark:bg-[#1a2c2c] text-[#568f8c] hover:bg-[#e9f2f1] hover:text-[#0f1a19] dark:hover:text-white border border-transparent hover:border-primary/20'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
            <div className="relative w-full md:w-80 group">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <span className="material-symbols-outlined text-[#568f8c] group-focus-within:text-primary transition-colors">search</span>
              </div>
              <input 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="block w-full pl-10 pr-3 py-2.5 border-none rounded-xl bg-white dark:bg-[#1a2c2c] text-[#0f1a19] dark:text-white placeholder-[#568f8c] focus:ring-2 focus:ring-primary/50 text-sm shadow-sm transition-all" 
                placeholder="Search by keyword, campaign..." 
                type="text"
              />
              <div className="absolute inset-y-0 right-0 pr-2 flex items-center">
                <button 
                  onClick={() => handleAction('Open filters', 'Filter Menu')}
                  className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors text-[#568f8c]"
                >
                  <span className="material-symbols-outlined text-[20px]">tune</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto px-8 pb-12 pt-4 scroll-smooth sidebar-scroll">
        <div className="max-w-[1400px] mx-auto">
          {filteredItems.length > 0 ? (
            <div className="columns-1 sm:columns-2 lg:columns-3 xl:columns-4 gap-6 space-y-6 pb-20">
              {filteredItems.map((item) => (
                <div 
                  key={item.id} 
                  onClick={() => onAssetClick?.(item)}
                  className="break-inside-avoid relative group rounded-xl overflow-hidden bg-white dark:bg-[#1a2c2c] shadow-sm hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-primary cursor-pointer"
                >
                  {item.isText ? (
                    <div className="p-6 flex flex-col h-full justify-between gap-4">
                      <div className="flex items-start justify-between">
                        <span className={`text-[10px] font-bold px-2 py-1 rounded-md uppercase tracking-wide ${
                          item.tag === 'EMAIL' ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300' : 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300'
                        }`}>
                          {item.tag}
                        </span>
                        <button 
                          onClick={(e) => { e.stopPropagation(); handleAction('Copy to clipboard', item.title); }}
                          className="material-symbols-outlined text-[#568f8c] text-lg hover:text-primary transition-colors"
                        >
                          content_copy
                        </button>
                      </div>
                      <div>
                        <h3 className="text-[#0f1a19] dark:text-white font-bold text-lg mb-2">{item.title}</h3>
                        <p className={`text-[#568f8c] dark:text-gray-300 text-sm leading-relaxed ${item.tag === 'COPY' ? 'italic font-serif line-clamp-4' : 'font-sans line-clamp-4'}`}>
                          {item.content}
                        </p>
                      </div>
                      <div className="pt-2 border-t border-gray-100 dark:border-gray-800 flex justify-between items-center">
                        <span className="text-xs text-gray-400">{item.meta}</span>
                        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button onClick={(e) => { e.stopPropagation(); handleAction('Share', item.title); }} className="text-[#568f8c] hover:text-primary"><span className="material-symbols-outlined text-lg">share</span></button>
                          <button onClick={(e) => { e.stopPropagation(); handleAction('Edit', item.title); }} className="text-[#568f8c] hover:text-primary"><span className="material-symbols-outlined text-lg">edit</span></button>
                        </div>
                      </div>
                    </div>
                  ) : item.type === 'Ad Videos' ? (
                    <div className="relative w-full aspect-[9/16] bg-black">
                      <img className="w-full h-full object-cover opacity-80 group-hover:opacity-60 transition-opacity" alt={item.title} src={item.url}/>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div 
                          className="w-14 h-14 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-all duration-300 shadow-lg border border-white/30"
                        >
                          <span className="material-symbols-outlined text-white text-4xl ml-1 group-hover:text-black">play_arrow</span>
                        </div>
                      </div>
                      {item.duration && <div className="absolute bottom-3 right-3 bg-black/60 text-white text-xs font-bold px-2 py-1 rounded backdrop-blur-sm">{item.duration}</div>}
                      <div className="absolute bottom-4 left-4 right-4 translate-y-4 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300 z-20 flex gap-2">
                        <button onClick={(e) => { e.stopPropagation(); handleAction('Quick View', item.title); }} className="flex-1 bg-white text-black py-2 rounded-lg text-xs font-bold shadow-lg hover:bg-gray-100 active:scale-95 transition-all">Quick View</button>
                        <button onClick={(e) => { e.stopPropagation(); handleAction('Share', item.title); }} className="flex-1 bg-primary text-black py-2 rounded-lg text-xs font-bold shadow-lg hover:bg-opacity-90 active:scale-95 transition-all">Share</button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="w-full h-auto">
                        <img className="w-full h-auto object-cover" alt={item.title} src={item.url}/>
                      </div>
                      <div className="p-4">
                        <div className="flex justify-between items-start mb-1">
                          <h3 className="text-[#0f1a19] dark:text-white font-bold text-base">{item.title}</h3>
                          <span className="bg-[#e9f2f1] text-[#0f1a19] text-[10px] font-bold px-2 py-1 rounded-md uppercase tracking-wide">{item.tag}</span>
                        </div>
                        <p className="text-[#568f8c] text-xs">{item.meta}</p>
                      </div>
                      <div className="absolute inset-0 bg-primary/90 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col items-center justify-center gap-3 backdrop-blur-sm z-10">
                        <button 
                          onClick={(e) => { e.stopPropagation(); handleAction('Download', item.title); }}
                          className="bg-white text-[#0f1a19] hover:text-primary w-36 py-2 rounded-lg font-bold text-sm shadow-lg transform hover:scale-105 transition-all flex items-center justify-center gap-2"
                        >
                          <span className="material-symbols-outlined text-lg">download</span> Download
                        </button>
                        <button 
                          onClick={(e) => { e.stopPropagation(); handleAction('Re-edit', item.title); }}
                          className="bg-white/20 text-white hover:bg-white hover:text-primary w-36 py-2 rounded-lg font-bold text-sm border border-white transition-all flex items-center justify-center gap-2"
                        >
                          <span className="material-symbols-outlined text-lg">edit</span> Re-edit
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-32 text-center">
              <span className="material-symbols-outlined text-6xl text-gray-300 mb-4">search_off</span>
              <h3 className="text-xl font-bold text-gray-400">No assets found</h3>
              <p className="text-gray-400">Try adjusting your filters or search query.</p>
            </div>
          )}

          {filteredItems.length > 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-center opacity-60 hover:opacity-100 transition-opacity">
              <button 
                onClick={() => handleAction('Loading more assets', 'Infinite Scroll')}
                className="w-16 h-16 rounded-full bg-[#e9f2f1] dark:bg-[#2a3c3c] flex items-center justify-center mb-4 active:scale-95 transition-all"
              >
                <span className="material-symbols-outlined text-primary text-3xl">expand_more</span>
              </button>
              <p className="text-[#568f8c] font-medium text-sm">Load more assets</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Gallery;
