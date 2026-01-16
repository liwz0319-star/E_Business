
import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Hero from './components/Hero';
import QuickActions from './components/QuickActions';
import GeminiResult from './components/GeminiResult';
import PricingModal from './components/PricingModal';
import Gallery from './components/Gallery';
import Templates from './components/Templates';
import Projects from './components/Projects';
import Editor from './components/Editor';
import Assets from './components/Assets';
import Insights from './components/Insights';
import Settings from './components/Settings';
import HelpSupport from './components/HelpSupport';
import AssetDetail from './components/AssetDetail';
import VideoDetail from './components/VideoDetail';
import ImageDetail from './components/ImageDetail';
import ProjectTimeline from './components/ProjectTimeline';
import { generateContent, GenerationType } from './services/geminiService';

export type AppView = 'home' | 'gallery' | 'templates' | 'projects' | 'editor' | 'assets' | 'insights' | 'settings' | 'help-support' | 'asset-detail' | 'video-detail' | 'image-detail' | 'project-timeline';

const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [currentView, setCurrentView] = useState<AppView>('home');
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<{ type: GenerationType; content: string | string[] } | null>(null);
  const [isPricingModalOpen, setIsPricingModalOpen] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<any>(null);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const handleGenerate = async (type: GenerationType = GenerationType.TEXT) => {
    if (!prompt.trim()) return;
    
    setIsGenerating(true);
    setResult(null);
    
    try {
      const response = await generateContent(prompt, type);
      setResult({ type, content: response });
    } catch (error) {
      console.error("Generation failed:", error);
      alert("Failed to generate content. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleQuickAction = (actionPrompt: string, type: GenerationType) => {
    setPrompt(actionPrompt);
    setTimeout(() => handleGenerate(type), 100);
  };

  const navigateTo = (view: AppView) => {
    setCurrentView(view);
    setResult(null);
    setPrompt('');
  };

  const openAssetDetail = (asset: any) => {
    setSelectedAsset(asset);
    
    // Check for timeline request explicitly
    if (asset.viewTimeline) {
      setCurrentView('project-timeline');
      return;
    }

    // Robust check for video types across different views
    const isVideo = 
      asset.type?.toLowerCase().includes('video') || 
      asset.tag === 'VIDEO' ||
      !!asset.duration;

    if (isVideo) {
      setCurrentView('video-detail');
    } else if (
      asset.type?.toLowerCase().includes('image') || 
      asset.type === 'template' || 
      asset.tag === 'IMG' ||
      (asset.url && !asset.duration)
    ) {
      setCurrentView('image-detail');
    } else {
      // Default detail view for projects, copy, or archives
      setCurrentView('asset-detail');
    }
  };

  const featuredCreations = [
    { title: "Summer Scent V1", type: "image", url: "https://lh3.googleusercontent.com/aida-public/AB6AXuCpSlHIN1IKvTeY0mdkVRYVCoTOjXPDgQOK8XlWMRcSCL3nS1mle71siP_jAKAWG5uypzOWxP1R3yaTWXO4DRPWe5GiazkUobAJlHXuAdMm64W6GQWgShc4QRlpBZJigcRpOt_8MhqSqwiJENt3GWVkFIj73azd8IpcHoscdcr1l4Pv4Q7G85KD2ZMoIGD_bi_FkH8bSSThxFSQ4naIr3ELXD0SS_hv5sGLzam0geA_lYQup95v_tCeNvlZ8ttpCQugs60NQB9vIfs" },
    { title: "Eco Runner X", type: "image", url: "https://lh3.googleusercontent.com/aida-public/AB6AXuBA6W_bdhwyeJqUpYJkmJlVjsowZdbWB_oJeJcwjB28z4Bs8qxelX7SZIlg4zfOmrTtAtjicwpLE_z-N-2mAj0fLg3ANis61sKlmmIWKZIw33c_z9k6CfhxfNqYx8eY3OqT7tXUlpD6SNiRMbYLL3pFLmve98_th73HCuK-oWAg-sBf83kyQ4YA8Z9Biv316EFFExHcsIsyhZRZOjap9fO6Mwfd1gWL_b-J7Vix_L_men7ueQBDyaOxJyQSmeUhUtfie0SiWF7bcP8" },
    { title: "Gold Chrono Ad", type: "video", url: "https://lh3.googleusercontent.com/aida-public/AB6AXuBB6lRQ08RMcVH2ZZFXabnso_kByRfBmPXfMmNoee5qHGyPM8sr69mbOu2mFwpSExRL60TktOoPs17NPymBrV4UfkjiwseaSlWPSSW0f96hnqUduth2kFwvEyX4nkWcVwiJ2x1YB_RVM1u2fb66jz9LALhubF8bC10Vh0U4pDBmVdRnuGNeaAZSxcftmk7r-MIOO3RNFjVpKXtZ6Z5Spuqbb5M6BrvV4x4TBwvEjf_pIUiLY-EmO0K84b5dPCDwXxQFAQe5jrRU_eQ", duration: "0:15" },
    { title: "Organic Coffee", type: "image", url: "https://lh3.googleusercontent.com/aida-public/AB6AXuC4iVG0jO1wf8LsxoFHR77m6d18HWs63bLBifMuLxQ-tnsm-XvbfutHYEz5bmfTB3U0W7JLQ8-O2DEUyHUc1OOFsYL6IdgivB0D7nibOjhImtq0FHy3PBbeQohPb8w-Pzp7B-5U3BxMY3rB8IFlX4cPiCXt70HiynQjf9xhou_wR6QQR_LV2mr9kzQAbTyA8kpYO3oH6KVJO7Ujx1nhKrZz520ZgaKopSziRTdzfubaApQZYfUXQFh_w26bf_zk8MDNnkxBkcir8wo" }
  ];

  return (
    <div className="flex h-screen w-full transition-colors duration-300 bg-background-light dark:bg-background-dark font-display overflow-hidden text-text-main dark:text-white">
      <Sidebar 
        currentView={currentView}
        onNavigate={navigateTo}
        onProjectClick={openAssetDetail}
        onUpgradeClick={() => setIsPricingModalOpen(true)}
        selectedProjectName={selectedAsset?.title}
      />
      
      <main className="flex-1 flex flex-col relative overflow-hidden">
        {currentView === 'home' && (
          <div className="flex-1 flex flex-col overflow-y-auto sidebar-scroll relative">
            <div className="absolute inset-0 pointer-events-none aurora-gradient opacity-50"></div>
            
            <Header darkMode={darkMode} onToggleDarkMode={() => setDarkMode(!darkMode)} />
            
            <div className="flex flex-col items-center justify-center px-6 py-12 space-y-12 z-10">
              <Hero />
              
              <div className="w-full max-w-2xl relative group animate-fade-in-up">
                <div className="absolute -inset-1 bg-gradient-to-r from-primary to-teal-400 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
                <div className="relative flex items-center bg-white dark:bg-slate-800 rounded-xl shadow-2xl p-2 border border-slate-100 dark:border-slate-700">
                  <button className="p-3 text-slate-400 hover:text-primary transition-colors">
                    <span className="material-icons-round">add_photo_alternate</span>
                  </button>
                  <input 
                    className="w-full bg-transparent border-none focus:ring-0 text-slate-800 dark:text-white placeholder-slate-400 text-lg px-2 h-12"
                    placeholder="Describe the e-commerce asset you need..." 
                    type="text"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
                  />
                  <button 
                    onClick={() => handleGenerate()}
                    disabled={isGenerating || !prompt.trim()}
                    className="bg-primary hover:bg-secondary text-slate-900 px-6 py-3 rounded-lg shadow-lg font-bold transition-all transform hover:scale-105 active:scale-95 flex items-center gap-2"
                  >
                    <span className="material-icons-round text-sm">auto_awesome</span>
                    <span>Generate</span>
                  </button>
                </div>
              </div>

              <div className="animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
                <QuickActions onAction={handleQuickAction} />
              </div>

              {result ? (
                 <div className="w-full max-w-4xl animate-fade-in-up">
                    <GeminiResult 
                      isGenerating={isGenerating} 
                      result={result} 
                      onReset={() => {
                          setResult(null);
                          setPrompt('');
                      }} 
                      onImageClick={(content) => openAssetDetail({ title: 'Generated Asset', url: content, type: result.type === GenerationType.VIDEO ? 'video' : 'image' })}
                    />
                 </div>
              ) : (
                <div className="w-full max-w-6xl space-y-6 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                  <div className="flex items-center justify-between px-2">
                    <h3 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                      <span className="material-symbols-outlined text-primary">auto_awesome_motion</span>
                      Inspiration Showcase
                    </h3>
                    <button onClick={() => navigateTo('gallery')} className="text-sm font-bold text-primary hover:text-teal-500 transition-colors">Explore Gallery</button>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                    {featuredCreations.map((item, i) => (
                      <div 
                        key={i} 
                        onClick={() => openAssetDetail(item)}
                        className="group relative rounded-2xl overflow-hidden bg-white dark:bg-slate-800 aspect-[3/4] shadow-sm border border-slate-100 dark:border-slate-700 cursor-pointer hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
                      >
                        <img className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" src={item.url} alt={item.title} />
                        <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-4">
                          <p className="text-white text-sm font-bold truncate">{item.title}</p>
                          <p className="text-primary-light text-[10px] uppercase font-black tracking-widest">{item.type}</p>
                        </div>
                        {item.type === 'video' && (
                          <div className="absolute inset-0 flex items-center justify-center">
                            <span className="material-symbols-outlined text-white text-4xl opacity-80 drop-shadow-md">play_circle</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="mt-auto py-12 text-center">
              <p className="text-xs text-slate-400 dark:text-slate-500 flex items-center justify-center gap-1 font-medium">
                <span className="material-icons-round text-[14px]">info</span>
                CommerceAI uses advanced Gemini models for generation.
              </p>
            </div>
          </div>
        )}

        {currentView === 'gallery' && (
          <Gallery onGenerateNew={() => navigateTo('home')} onAssetClick={openAssetDetail} />
        )}

        {currentView === 'templates' && (
          <Templates onAssetClick={openAssetDetail} />
        )}

        {currentView === 'projects' && (
          <Projects onNewProject={() => navigateTo('home')} onAssetClick={openAssetDetail} />
        )}

        {currentView === 'editor' && (
          <Editor darkMode={darkMode} onToggleDarkMode={() => setDarkMode(!darkMode)} onAssetClick={openAssetDetail} />
        )}

        {currentView === 'assets' && (
          <Assets onGenerate={() => navigateTo('home')} onAssetClick={openAssetDetail} />
        )}

        {currentView === 'insights' && (
          <Insights />
        )}

        {currentView === 'settings' && (
          <Settings />
        )}

        {currentView === 'help-support' && (
          <HelpSupport />
        )}

        {currentView === 'asset-detail' && (
          <AssetDetail 
            asset={selectedAsset} 
            onBack={() => navigateTo('projects')} 
            onAssetClick={openAssetDetail}
          />
        )}

        {currentView === 'video-detail' && (
          <VideoDetail 
            video={selectedAsset} 
            onClose={() => navigateTo('gallery')} 
          />
        )}

        {currentView === 'image-detail' && (
          <ImageDetail 
            image={selectedAsset} 
            onClose={() => navigateTo('gallery')} 
          />
        )}

        {currentView === 'project-timeline' && (
          <ProjectTimeline 
            project={selectedAsset}
            onBack={() => navigateTo('projects')}
          />
        )}
      </main>

      {isPricingModalOpen && (
        <PricingModal onClose={() => setIsPricingModalOpen(false)} />
      )}
    </div>
  );
};

export default App;
