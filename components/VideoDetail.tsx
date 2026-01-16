
import React, { useState } from 'react';

interface VideoDetailProps {
  video: any;
  onClose: () => void;
}

const VideoDetail: React.FC<VideoDetailProps> = ({ video, onClose }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(45);
  const [volume, setVolume] = useState(80);

  const handleAction = (label: string) => {
    alert(`Video Action: ${label}`);
  };

  const skipTime = (seconds: number) => {
    // Mock seeking logic
    const newProgress = Math.min(100, Math.max(0, progress + (seconds * 2))); 
    setProgress(newProgress);
    console.log(`Seeking ${seconds}s... New progress: ${newProgress}%`);
  };

  return (
    <div className="fixed inset-0 z-50 bg-[#f8fafc] dark:bg-[#0f172a] font-display flex flex-col h-full overflow-hidden transition-colors">
      {/* Background Overlay Backdrop */}
      <div className="absolute inset-0 bg-slate-900/10 backdrop-blur-sm pointer-events-none"></div>

      {/* Main Container */}
      <div className="relative z-10 w-full max-w-[1400px] mx-auto bg-white dark:bg-[#1e293b] shadow-2xl flex flex-col h-full ring-1 ring-black/5 dark:ring-white/5 transition-colors">
        
        {/* Header */}
        <div className="flex items-center justify-between px-8 py-5 border-b border-slate-100 dark:border-slate-800 shrink-0">
          <div className="flex flex-col">
            <h1 className="text-slate-900 dark:text-white text-xl font-bold tracking-tight">{video?.title || 'AI Generated Ad Preview'}</h1>
            <p className="text-slate-500 dark:text-slate-400 text-sm">Summer Campaign 2024 • V3</p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all transform hover:rotate-90"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <div className="flex flex-col lg:flex-row flex-1 overflow-hidden h-full">
          {/* Left Column: Video Player */}
          <div className="flex-1 bg-slate-50 dark:bg-slate-900/50 p-6 lg:p-12 flex flex-col justify-center items-center overflow-y-auto sidebar-scroll transition-colors">
            <div className="w-full max-w-4xl flex flex-col gap-6">
              <div className="relative group rounded-2xl overflow-hidden bg-black aspect-video shadow-2xl ring-1 ring-white/10">
                <div 
                  className="absolute inset-0 bg-cover bg-center transition-transform duration-1000 group-hover:scale-105" 
                  style={{ backgroundImage: `url('${video?.url || video?.image || 'https://lh3.googleusercontent.com/aida-public/AB6AXuBB6lRQ08RMcVH2ZZFXabnso_kByRfBmPXfMmNoee5qHGyPM8sr69mbOu2mFwpSExRL60TktOoPs17NPymBrV4UfkjiwseaSlWPSSW0f96hnqUduth2kFwvEyX4nkWcVwiJ2x1YB_RVM1u2fb66jz9LALhubF8bC10Vh0U4pDBmVdRnuGNeaAZSxcftmk7r-MIOO3RNFjVpKXtZ6Z5Spuqbb5M6BrvV4x4TBwvEjf_pIUiLY-EmO0K84b5dPCDwXxQFAQe5jrRU_eQ'}')` }}
                >
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-60"></div>
                </div>

                {/* Central Play Button */}
                {!isPlaying && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <button 
                      onClick={() => setIsPlaying(true)}
                      className="flex items-center justify-center size-24 rounded-full bg-primary/90 text-slate-900 hover:bg-primary hover:scale-110 transition-all shadow-glow backdrop-blur-md animate-fade-in"
                    >
                      <span className="material-symbols-outlined !text-[48px] ml-1.5" style={{ fontVariationSettings: "'FILL' 1" }}>play_arrow</span>
                    </button>
                  </div>
                )}

                {/* Video Controls Overlay */}
                <div className="absolute inset-x-0 bottom-0 p-6 bg-gradient-to-t from-black/90 to-transparent pt-16 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className="group/progress relative h-1.5 bg-white/30 rounded-full cursor-pointer hover:h-2.5 transition-all mb-4">
                    <div className="absolute h-full bg-primary rounded-full" style={{ width: `${progress}%` }}>
                      <div className="absolute right-0 top-1/2 -translate-y-1/2 size-3.5 bg-white rounded-full shadow-lg opacity-0 group-hover/progress:opacity-100 transform scale-0 group-hover/progress:scale-100 transition-all"></div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-white">
                    <div className="flex items-center gap-5">
                      <button 
                        onClick={() => setIsPlaying(!isPlaying)}
                        className="hover:text-primary transition-colors"
                      >
                        <span className="material-symbols-outlined !text-[28px]" style={{ fontVariationSettings: isPlaying ? "'FILL' 1" : "" }}>
                          {isPlaying ? 'pause' : 'play_arrow'}
                        </span>
                      </button>
                      <span className="text-sm font-bold tracking-tight tabular-nums drop-shadow-md">0:15 / 0:33</span>
                      <button onClick={() => setVolume(volume === 0 ? 80 : 0)} className="hover:text-primary transition-colors">
                        <span className="material-symbols-outlined">{volume === 0 ? 'volume_off' : 'volume_up'}</span>
                      </button>
                    </div>
                    <div className="flex items-center gap-5">
                      <button onClick={() => handleAction('Settings')} className="hover:text-primary transition-colors">
                        <span className="material-symbols-outlined">settings</span>
                      </button>
                      <button onClick={() => handleAction('Fullscreen')} className="hover:text-primary transition-colors">
                        <span className="material-symbols-outlined">fullscreen</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Player Metadata & Quick Tools */}
              <div className="flex justify-between items-center px-2">
                <div className="flex gap-3">
                  <span className="inline-flex items-center rounded-lg bg-white dark:bg-slate-800 px-3 py-1.5 text-xs font-bold text-slate-700 dark:text-slate-300 ring-1 ring-inset ring-slate-200 dark:ring-slate-700 shadow-sm">HD 1080p</span>
                  <span className="inline-flex items-center rounded-lg bg-white dark:bg-slate-800 px-3 py-1.5 text-xs font-bold text-slate-700 dark:text-slate-300 ring-1 ring-inset ring-slate-200 dark:ring-slate-700 shadow-sm">Landscape</span>
                </div>
                <div className="flex gap-6 text-sm text-slate-500 dark:text-slate-400 font-bold">
                  <button onClick={() => skipTime(-10)} className="flex items-center gap-1.5 hover:text-primary transition-colors active:scale-90">
                    <span className="material-symbols-outlined text-[20px]">replay_10</span>
                    <span>-10s</span>
                  </button>
                  <button onClick={() => skipTime(10)} className="flex items-center gap-1.5 hover:text-primary transition-colors active:scale-90">
                    <span>+10s</span>
                    <span className="material-symbols-outlined text-[20px]">forward_10</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Settings & Assets */}
          <div className="w-full lg:w-[420px] border-l border-slate-100 dark:border-slate-800 bg-white dark:bg-[#1e293b] flex flex-col h-full transition-colors">
            <div className="flex-1 overflow-y-auto sidebar-scroll p-8 space-y-10">
              {/* Creative Assets List */}
              <div>
                <h3 className="text-slate-900 dark:text-white text-sm font-black uppercase tracking-[0.1em] mb-5 flex items-center gap-3">
                  <span className="material-symbols-outlined text-primary text-[20px]">perm_media</span>
                  Creative Assets Used
                </h3>
                <div className="space-y-3">
                  <div onClick={() => handleAction('Preview Source')} className="group flex items-center gap-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-800 border border-transparent hover:border-primary/30 transition-all cursor-pointer shadow-sm">
                    <div className="size-14 rounded-lg bg-cover bg-center shrink-0 border border-slate-200 dark:border-slate-700 shadow-sm" style={{ backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuD1spuVPahF-IXITPXB06xokTuxZz4U8wSh5oqNM-D2dF3GDLJTtzW2bhUJQMgCuMUQDwGDOCWXxfFKal2msnjgFCxoIwjbfMBsPc6ZelweYSMOtLCrdK8yafzqiZPzjplfAAsoRYL3sD770T-J4gkJb_CEUESy2Lk0KdpmObVGlmvDCT76DDg1hMZmgVyX68TSpYCnaIa2Jh-DYIWXa_n5mtgyDZdV_RtQoev-buzDvzVjJ2Mz0IGzkrhmjX4dd7MM-oqD3Njz46Q')" }}></div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-bold text-slate-900 dark:text-white truncate">Main Product Shot.jpg</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Source Image</p>
                    </div>
                    <span className="material-symbols-outlined text-slate-400 group-hover:text-primary transition-colors">visibility</span>
                  </div>
                  <div onClick={() => handleAction('Open BGM Selector')} className="group flex items-center gap-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-800 border border-transparent hover:border-primary/30 transition-all cursor-pointer shadow-sm">
                    <div className="size-14 rounded-lg bg-primary/10 flex items-center justify-center shrink-0 text-primary border border-primary/20">
                      <span className="material-symbols-outlined text-3xl">music_note</span>
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-bold text-slate-900 dark:text-white truncate">Summer Vibes Pop</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Background Music</p>
                    </div>
                    <button onClick={(e) => { e.stopPropagation(); handleAction('Change Music'); }} className="text-xs font-extrabold text-primary hover:text-teal-400">Change</button>
                  </div>
                  <div className="group flex items-start gap-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-800 border border-transparent hover:border-primary/30 transition-all cursor-pointer shadow-sm">
                    <div className="size-14 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 flex items-center justify-center shrink-0 text-indigo-500 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-900/30">
                      <span className="material-symbols-outlined text-3xl">text_fields</span>
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-bold text-slate-900 dark:text-white mb-1">Generated Script</p>
                      <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed italic">
                        "Step into summer with the new AirMax series. Lightweight, breathable, and made for movement..."
                      </p>
                    </div>
                    <button onClick={(e) => { e.stopPropagation(); handleAction('Copy Script'); }} className="text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">
                      <span className="material-symbols-outlined text-[20px]">content_copy</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Generation Settings Panel */}
              <div>
                <h3 className="text-slate-900 dark:text-white text-sm font-black uppercase tracking-[0.1em] mb-5 flex items-center gap-3">
                  <span className="material-symbols-outlined text-primary text-[20px]">tune</span>
                  Generation Settings
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Tone</p>
                    <p className="text-sm font-bold text-slate-900 dark:text-white">Energetic</p>
                  </div>
                  <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Duration</p>
                    <p className="text-sm font-bold text-slate-900 dark:text-white">30s</p>
                  </div>
                  <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 col-span-2">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Target Audience</p>
                    <p className="text-sm font-bold text-slate-900 dark:text-white">Gen Z, Fitness Enthusiasts</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Sticky Bottom Actions */}
            <div className="p-8 border-t border-slate-100 dark:border-slate-800 bg-white dark:bg-[#1e293b] shrink-0">
              <div className="flex flex-col gap-4">
                <button 
                  onClick={() => handleAction('Export Video')}
                  className="w-full flex items-center justify-center gap-3 bg-primary hover:bg-teal-400 text-slate-900 font-black py-4 px-6 rounded-xl transition-all shadow-xl shadow-primary/20 transform hover:-translate-y-0.5 active:translate-y-0 active:scale-95"
                >
                  <span className="material-symbols-outlined font-bold">download</span>
                  Export for TikTok / Reels
                </button>
                <div className="grid grid-cols-2 gap-4">
                  <button 
                    onClick={() => handleAction('Open BGM Selector')}
                    className="flex items-center justify-center gap-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-bold py-3 px-4 rounded-xl transition-all shadow-sm active:scale-95"
                  >
                    <span className="material-symbols-outlined text-[20px]">music_cast</span>
                    Change BGM
                  </button>
                  <button 
                    onClick={() => handleAction('Open Script Editor')}
                    className="flex items-center justify-center gap-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-bold py-3 px-4 rounded-xl transition-all shadow-sm active:scale-95"
                  >
                    <span className="material-symbols-outlined text-[20px]">edit_note</span>
                    Edit Script
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoDetail;
