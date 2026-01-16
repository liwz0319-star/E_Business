
import React, { useState, useMemo } from 'react';

interface AssetDetailProps {
  asset: any;
  onBack: () => void;
  onAssetClick?: (asset: any) => void;
}

const AssetDetail: React.FC<AssetDetailProps> = ({ asset, onBack, onAssetClick }) => {
  const [activeFilter, setActiveFilter] = useState('All items');
  const projectTitle = asset?.title || 'Summer Campaign';

  // 模拟不同项目的历史数据存储
  const projectData: Record<string, any[]> = {
    "Summer Campaign": [
      { id: 101, name: 'Summer Vibes Promo.mp4', type: 'video', size: '45 MB', time: '2 hours ago', url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBq_XZiRRPV-m9CWdTTNFOARqiOfUToD5sr2vMH4gcQyaIiEwOpWXJSepBcZpY-AuLBkjeYP3Kv3KrAJjRgzgxjVjGfBXZ50YzCMvFpy_pzTk4ptnLGGhQfUg7tGq9_bk_8ayamCKVwhu4OUlraAOIuUA59O8pS0fdT09QeBBKGtNe70I8zLVVMdc756Wurej3CQKXaj6-E9Sistv-CXxXHiPQdFZOptFusYWbSUqqSBVjqTot3JfhdBokLQbbXEHokeExxWAeMYxQ', duration: '0:15' },
      { id: 102, name: 'Sunscreen Splash.png', type: 'image', size: '2.4 MB', time: '4 hours ago', url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuD_XP25G3DpvzY41TzpYqhwsOTyf6yUBnc4BRbPG0TM0YLIGOgO2v7GwGqSn0obslYgU4jdz6RwjeSXB3AJdtKxFI_NeO1C_kGK-yz6h2MLWBX2a1N2Iz0NXqKrU7msDmUQEmyoHVmgyUO0zbwvDfdWNh8l6lnlcOYJLBVv5PpeO8I_pnEOwFK97YJ1k6wVZeLrpUWUjCnF2lydbAescSYRRjyj-Ok7pEP0aE7Vxz_2rF7J-zwVmxMy0nTLhZ-gd1o3Ge7-oJx0Auw' },
      { id: 103, name: 'IG Story Copy - Draft 1', type: 'copy', time: 'Yesterday', content: '"Get that golden glow without the burn! ☀️ Our new SPF 50 protects & hydrates. #SummerEssentials #GlowUp..."' },
      { id: 104, name: 'Beach Background v2.png', type: 'image', size: '5.1 MB', time: '2 days ago', url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCx63xn54F7zmOd4cBbu15eMsktimdLe7oKTo9oEU-AJfPjWm4-FqArfN78N62CSZJvdCZo8A-sWOvKLp4ercS_K83jv1L9HmrPM2W6Wt3_02vFzX8KklcsX26XSslHEKrwhdiM4EqIrP_66rOSAgaqTz0zQh_ICQ5itgfl45xzQV3GOQRD197dnxG9rrXybleLPOsxap4t6z561Tb3ImnTYdNNtqKRQ3S1fCxltX6wO_nyU8A0u7_gNM-oeqJRvJPfa-Fwk1puvZ0', isGenerated: true },
      { id: 105, name: 'Story Teaser.mp4', type: 'video', size: '12 MB', time: '3 days ago', url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuD9qsJwC2mpRSParJ_tYy63x0eUfPRcj3MTfuTMIWTSRdlgzrsv2OWiqSW94S4B4VS3Pz_AopKbNci1z6zneSM8-Wo5W344Y9kP2aO08p_lZW2nMbVl-Z9ga524tAll3AbfXbUU_wi93BXSYa6tPIcERzx4Od8Nb1iTC72B0lXk6XpXhXBLK9hXmetTltfyq8SmXm8iOwnuShcVK6brUTaLO3NOL0Lii4TK2ofaIJGaNVJ__5DgEZCLeF4EdVU-wcK6Y7t52l2I5dQ', duration: '0:06' },
      { id: 106, name: 'Raw Assets Archive', type: 'archive', size: '1.2 GB', time: '1 week ago' }
    ],
    "Nike Air Promo": [
      { id: 201, name: 'Nike Air Max Gen 2.png', type: 'image', size: '3.8 MB', time: '5 hours ago', url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDtAU4Euz9lCVjEtNHvP_8x80eLZpAotsGlAzQPWGK7wSw1cXmkooHfPIBgKCnZScrX0vpr9EmEmvelbwQ6YCu3hdIiR299BDuKAgguBOZ9sTSOj1u41YN4EVPKVBeQ_duDqWuwhuoLEUvR9EOt_fz1aOHZHETQVESPhJ9Sjk32T_J0ALpdtHmUfwB6s0XQvIyn5i0RNcwtFxpoIQyimRQwsCBqst8gk70P1uW9j01mTF_U7z5mHCeYgRhZZLMd425070UL7lC0aj8', isGenerated: true },
      { id: 202, name: 'Product Reveal.mp4', type: 'video', size: '82 MB', time: 'Yesterday', url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDOsNo_8An-UkDwEV1h5cBmy-z2nCejF-VhfD7T9uwX1KPm5uYnWlkuOclGwb2ILhR4OGgVMhxL-sbE9qJd4vUyMInZ1nxiSpQJhiUmM0km01pfmdd4rDQCZoIACezl2yb-GK_wRohh_rneG4-WCgoP2IcZpbr43OqsPatVis3w-8Dn3zcdW1mkq-cB0kumesFO33EAeybjnC53yPoI_6tolI5j3-EGOJt3d-FsL0BSHdWnlD34c_dPXjmeQ4QqCWNyBAIMzdZXeKM', duration: '0:30' },
      { id: 203, name: 'Facebook Ad Copy.txt', type: 'copy', time: '2 days ago', content: '"Experience the next level of comfort. The Air Max Gen 2 is now available in limited edition colors. Shop now and feel the bounce. #NikeAir #SneakerLaunch"' }
    ],
    "Organic Coffee Beans": [
      { id: 301, name: 'Morning Brew.jpg', type: 'image', size: '1.2 MB', time: '1 hour ago', url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCusrk-fGSMOjIPLv34G4cc0vDlzaFYmWwsg4ur48BogIpoXFLvKoblZ-EGLU_qiqf7IhX6PFzvCx55tbvl3qmuNZ7ugm5o6zszwhgYwJpT15udjk6sAdmE-ga2u3vx_4aclx42x02-AlUvt9pGOjmyLGnmqD78qd_-so56dKurxqwdusPsRyvi6BuxQJPhtlPBjaL7I0T8rtaAvWF6uxQRuSzJkgWmYYQecC17Xg5U51TMaSr4KTXVUJ0zs2fKIwn34XS96gZ0t4M' },
      { id: 302, name: 'Coffee Close-up.png', type: 'image', size: '4.5 MB', time: '3 hours ago', url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuC0WwhjGemC4Prst4wgDp3eOshTSGfcR--zRts79ROF8jMDjEUqNbfaOhDDfBg6XOON1ryswveIMrL5USShF4Cqd_NXeSA8VIWnV8FinlatB3YefTbb0Pbo9K0dqRhtO7dcnUBp6NHKm83tN6fl6NHF3jqjewqMRk1z_rRnyPEG144583xUAyxwaXzmmkOMKhoRgboaRqjVnqQTWOBIYCQvkXIiFM1LFr1zJzyP8dDLSEOjFTscaYPKzePrBZPwLqWj1Y-3luuyBzM', isGenerated: true },
      { id: 303, name: 'Rich Aroma Ad Script', type: 'copy', time: 'Yesterday', content: '"The smell of fresh morning is just one bean away. Organic, fair-trade, and roasted to perfection. Start your day right."' }
    ]
  };

  const currentFiles = useMemo(() => {
    const rawFiles = projectData[projectTitle] || projectData["Summer Campaign"];
    if (activeFilter === 'All items') return rawFiles;
    return rawFiles.filter(f => f.type === activeFilter.toLowerCase().slice(0, -1) || (activeFilter === 'Images' && f.type === 'image') || (activeFilter === 'Videos' && f.type === 'video'));
  }, [projectTitle, activeFilter]);

  const handleAction = (label: string) => {
    alert(`Action: ${label}`);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-background-light dark:bg-background-dark font-display transition-colors">
      {/* Header with Breadcrumbs */}
      <header className="bg-background-light dark:bg-background-dark shrink-0 px-8 pt-8 pb-4 z-10 transition-colors">
        <div className="max-w-7xl mx-auto flex flex-col gap-6">
          <div className="flex items-center gap-2 text-sm">
            <button 
              onClick={onBack}
              className="text-text-secondary hover:text-primary font-bold transition-colors uppercase tracking-widest text-[11px]"
            >
              Recent Projects
            </button>
            <span className="material-symbols-outlined text-text-secondary text-base">chevron_right</span>
            <span className="text-text-main dark:text-white font-bold">{projectTitle}</span>
          </div>
          
          <div className="flex flex-wrap items-center justify-between gap-4">
            <h1 className="text-text-main dark:text-white text-4xl font-black tracking-tight leading-none animate-fade-in-up">
              {projectTitle}
            </h1>
            <button 
              onClick={() => handleAction('New Creation')}
              className="flex items-center justify-center gap-2 rounded-xl h-12 px-6 bg-primary text-slate-900 hover:bg-teal-400 transition-all shadow-xl shadow-primary/20 font-black tracking-wide transform hover:scale-105 active:scale-95"
            >
              <span className="material-symbols-outlined font-bold">add_circle</span>
              <span>New Creation</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto px-8 pb-10 sidebar-scroll">
        <div className="max-w-7xl mx-auto flex flex-col h-full">
          
          {/* Filters & Toolbar */}
          <div className="flex flex-wrap items-center justify-between gap-4 mb-8 sticky top-0 bg-background-light/90 dark:bg-background-dark/90 backdrop-blur-sm py-4 z-10 border-b border-transparent transition-colors">
            <div className="flex gap-2 flex-wrap">
              {['All items', 'Images', 'Videos', 'Copy'].map((filter) => (
                <button 
                  key={filter}
                  onClick={() => setActiveFilter(filter)}
                  className={`flex h-10 items-center justify-center px-5 rounded-xl font-bold text-sm transition-all ${
                    activeFilter === filter 
                    ? 'bg-primary text-slate-900 shadow-lg shadow-primary/30 ring-1 ring-primary/50' 
                    : 'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-gray-300 hover:border-primary hover:text-primary'
                  }`}
                >
                  <span className="material-symbols-outlined text-[18px] mr-2">
                    {filter === 'All items' ? 'apps' : filter === 'Images' ? 'image' : filter === 'Videos' ? 'movie' : 'description'}
                  </span>
                  {filter}
                </button>
              ))}
            </div>
            
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-1 shadow-sm">
                <button className="p-2 rounded-lg bg-primary/10 text-primary transition-colors">
                  <span className="material-symbols-outlined text-xl font-bold">grid_view</span>
                </button>
                <button className="p-2 rounded-lg text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                  <span className="material-symbols-outlined text-xl">view_list</span>
                </button>
              </div>
              <div className="relative group">
                <select className="appearance-none bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-white h-11 pl-4 pr-10 rounded-xl text-sm font-bold focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent cursor-pointer shadow-sm">
                  <option>Sort by: Last edited</option>
                  <option>Sort by: Name</option>
                  <option>Sort by: Size</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-400">
                  <span className="material-symbols-outlined">expand_more</span>
                </div>
              </div>
            </div>
          </div>

          {/* Grid Content */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-20">
            {currentFiles.map((file, idx) => (
              <div 
                key={file.id} 
                onClick={() => onAssetClick?.(file)}
                style={{ animationDelay: `${idx * 0.05}s` }}
                className="group bg-white dark:bg-slate-800 rounded-2xl overflow-hidden border border-slate-100 dark:border-slate-700 hover:shadow-2xl hover:border-primary transition-all duration-300 flex flex-col cursor-pointer animate-fade-in-up"
              >
                <div className="aspect-[4/3] w-full relative overflow-hidden bg-slate-100 dark:bg-black">
                  {file.type === 'video' && (
                    <>
                      <img alt={file.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 opacity-90 group-hover:opacity-100" src={file.url} />
                      <div className="absolute inset-0 flex items-center justify-center bg-slate-900/30 group-hover:bg-slate-900/10 transition-colors">
                        <div className="size-14 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center border border-white/50 group-hover:scale-110 transition-transform shadow-xl">
                          <span className="material-symbols-outlined text-white text-4xl" style={{ fontVariationSettings: "'FILL' 1" }}>play_arrow</span>
                        </div>
                      </div>
                      <div className="absolute top-3 left-3 px-2 py-1 rounded-lg bg-slate-900/60 backdrop-blur-md text-white text-[10px] font-black tracking-wider">{file.duration}</div>
                    </>
                  )}
                  {file.type === 'image' && (
                    <img alt={file.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" src={file.url} />
                  )}
                  {file.type === 'copy' && (
                    <div className="aspect-[4/3] w-full relative overflow-hidden bg-[#fdfdfd] dark:bg-slate-900/50 flex flex-col p-6">
                      <div className="flex-1 overflow-hidden relative">
                        <p className="text-[10px] text-primary font-black uppercase tracking-[0.2em] mb-3">AI Engine Output</p>
                        <p className="text-sm text-slate-800 dark:text-slate-200 font-serif italic leading-relaxed line-clamp-5">
                          {file.content}
                        </p>
                        <div className="absolute bottom-0 left-0 w-full h-20 bg-gradient-to-t from-[#fdfdfd] dark:from-slate-800 to-transparent"></div>
                      </div>
                    </div>
                  )}
                  {file.type === 'archive' && (
                    <div className="aspect-[4/3] w-full relative overflow-hidden bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
                      <span className="material-symbols-outlined text-slate-300 dark:text-slate-700 text-7xl opacity-50 group-hover:scale-110 transition-transform">folder_zip</span>
                    </div>
                  )}
                  {file.isGenerated && (
                    <div className="absolute top-3 left-3 px-2 py-1 rounded-lg bg-primary text-slate-900 text-[10px] font-black shadow-lg flex items-center gap-1">
                      <span className="material-symbols-outlined text-[14px]">auto_awesome</span> PRO
                    </div>
                  )}
                  <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={(e) => { e.stopPropagation(); handleAction('Select File'); }} className="size-9 flex items-center justify-center rounded-full bg-white text-slate-900 shadow-xl hover:bg-primary transition-all active:scale-90">
                      <span className="material-symbols-outlined text-xl">check_circle</span>
                    </button>
                  </div>
                </div>
                
                <div className="p-4 flex flex-col gap-1 border-t border-slate-50 dark:border-slate-700 transition-colors">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2 overflow-hidden">
                      <div className={`p-1.5 rounded-lg ${file.type === 'video' ? 'bg-red-50 text-red-400' : file.type === 'image' ? 'bg-blue-50 text-blue-400' : 'bg-orange-50 text-orange-400'}`}>
                        <span className="material-symbols-outlined text-[18px] shrink-0">
                          {file.type === 'video' ? 'movie' : file.type === 'image' ? 'image' : file.type === 'copy' ? 'description' : 'folder'}
                        </span>
                      </div>
                      <h3 className="font-bold text-slate-900 dark:text-white text-sm truncate">{file.name}</h3>
                    </div>
                    <button onClick={(e) => { e.stopPropagation(); handleAction('File Options'); }} className="text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">
                      <span className="material-symbols-outlined text-xl">more_vert</span>
                    </button>
                  </div>
                  <div className="flex items-center justify-between text-[10px] font-bold text-slate-400 mt-1 uppercase tracking-wider">
                    <span>{file.size || 'TEXT'}</span>
                    <span>{file.time}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {currentFiles.length === 0 && (
            <div className="flex flex-col items-center justify-center py-32 text-center animate-fade-in-up">
              <span className="material-symbols-outlined text-7xl text-slate-200 dark:text-slate-800 mb-6">folder_off</span>
              <h3 className="text-xl font-bold text-slate-400">No matching files found</h3>
              <p className="text-slate-400">Try changing your filter or start a new generation.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AssetDetail;
