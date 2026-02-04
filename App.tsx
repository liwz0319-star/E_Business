
import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Hero from './components/Hero';
import GeminiResult from './components/GeminiResult';
import PricingModal from './components/PricingModal';
import UserProfileModal from './components/UserProfileModal';
import NotificationModal from './components/NotificationModal';
import Gallery from './components/Gallery';
import Insights from './components/Insights';
import Settings from './components/Settings';
import HelpSupport from './components/HelpSupport';
import Projects from './components/Projects';
import AssetDetail from './components/AssetDetail';
import VideoDetail from './components/VideoDetail';
import ImageDetail from './components/ImageDetail';
import ProjectTimeline from './components/ProjectTimeline';
import Login from './components/Login';
import Signup from './components/Signup';
import { generateContent, GenerationType } from './services/geminiService';

export type AppView = 'login' | 'signup' | 'home' | 'chat' | 'gallery' | 'insights' | 'settings' | 'help-support' | 'projects' | 'asset-detail' | 'video-detail' | 'image-detail' | 'project-timeline';

const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [currentView, setCurrentView] = useState<AppView>('login');
  const [prompt, setPrompt] = useState('');
  const [userMessage, setUserMessage] = useState<string | null>(null);
  const [sentUserImage, setSentUserImage] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeGenerationType, setActiveGenerationType] = useState<GenerationType | null>(null);
  const [result, setResult] = useState<{ type: GenerationType; content: string | string[]; title?: string } | null>(null);
  const [isPricingModalOpen, setIsPricingModalOpen] = useState(false);
  const [isUserProfileModalOpen, setIsUserProfileModalOpen] = useState(false);
  const [isNotificationModalOpen, setIsNotificationModalOpen] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<any>(null);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);

  const chatScrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Auto-scroll logic for chat
  useEffect(() => {
    if (currentView === 'chat' && chatScrollRef.current) {
      chatScrollRef.current.scrollTo({ top: chatScrollRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [isGenerating, result, currentView]);

  const handleGenerate = async (type: GenerationType = GenerationType.TEXT, overridePrompt?: string, overrideImage?: string) => {
    const finalPrompt = overridePrompt || prompt;
    if (!finalPrompt.trim()) return;

    // Use override image (from buttons) or uploaded image
    const imageToDisplay = overrideImage || uploadedImage;
    setSentUserImage(imageToDisplay);

    // If generating from home, switch to chat view immediately
    if (currentView === 'home') {
      setCurrentView('chat');
    }

    setResult(null);
    setUserMessage(finalPrompt);
    setIsGenerating(true);
    setActiveGenerationType(type);

    try {
      const response = await generateContent(finalPrompt, type);
      setResult({
        type,
        content: response,
        title: finalPrompt.length > 30 ? finalPrompt.substring(0, 30) + '...' : finalPrompt
      });
    } catch (error: any) {
      console.error("Generation failed:", error);
      alert("Failed to generate content. Please check your API key and try again.");
    } finally {
      setIsGenerating(false);
      setPrompt('');
      setUploadedImage(null);
    }
  };

  const handleNavigateToChat = (actionPrompt: string, type: GenerationType, imageUrl: string) => {
    handleGenerate(type, actionPrompt, imageUrl);
  };

  const navigateTo = (view: AppView) => {
    setCurrentView(view);
    if (view !== 'chat' && view !== 'login') {
      setResult(null);
      setUserMessage(null);
      setSentUserImage(null);
      setPrompt('');
      setUploadedImage(null);
    }
    setIsGenerating(false);
  };

  const openAssetDetail = (asset: any) => {
    setSelectedAsset(asset);
    if (asset.viewTimeline) {
      setCurrentView('project-timeline');
      return;
    }
    const isVideo = asset.type?.toLowerCase().includes('video') || asset.tag === 'VIDEO' || !!asset.duration;
    if (isVideo) {
      setCurrentView('video-detail');
    } else if (asset.type?.toLowerCase().includes('image') || asset.type === 'template' || asset.tag === 'IMG' || (asset.url && !asset.duration)) {
      setCurrentView('image-detail');
    } else {
      setCurrentView('asset-detail');
    }
  };

  const handleImageIconClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // If current view is login, render only the Login component
  if (currentView === 'login') {
    return <Login onLogin={() => navigateTo('home')} onSignup={() => navigateTo('signup')} />;
  }

  // If current view is signup, render only the Signup component
  if (currentView === 'signup') {
    return <Signup onSignIn={() => navigateTo('login')} />;
  }

  return (
    <div className="flex h-screen w-full transition-colors duration-300 bg-background-light dark:bg-background-dark font-display overflow-hidden text-text-main dark:text-white">
      <Sidebar
        currentView={currentView}
        onNavigate={navigateTo}
        onProjectClick={openAssetDetail}
        onUpgradeClick={() => setIsPricingModalOpen(true)}
        onProfileClick={() => setIsUserProfileModalOpen(true)}
        selectedProjectName={selectedAsset?.title}
      />

      <main className="flex-1 flex flex-col relative overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-primary/10 dark:bg-primary/5 rounded-full blur-[100px] -z-10 pointer-events-none"></div>

        {currentView !== 'chat' && (
          <Header
            darkMode={darkMode}
            onToggleDarkMode={() => setDarkMode(!darkMode)}
            onNotificationClick={() => setIsNotificationModalOpen(true)}
          />
        )}

        {currentView === 'home' && (
          <div className="flex-1 overflow-hidden px-8 pb-32">
            <div className="max-w-5xl mx-auto pt-12 flex flex-col items-center">
              <Hero />

              <div className="w-full max-w-2xl relative mb-12 group animate-fade-in-up">
                <div className="absolute inset-0 bg-primary/20 dark:bg-primary/10 rounded-2xl blur-lg group-hover:bg-primary/30 transition-all duration-500"></div>

                <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" className="hidden" />

                <div className="relative bg-white dark:bg-surface-dark rounded-2xl shadow-soft p-2 flex items-center border border-slate-100 dark:border-slate-700">
                  <span onClick={handleImageIconClick} className="material-icons-round text-slate-400 ml-4 mr-3 cursor-pointer hover:text-primary transition-colors">
                    add_photo_alternate
                  </span>
                  <input
                    className="flex-1 bg-transparent border-none focus:ring-0 text-slate-700 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 text-sm py-3"
                    placeholder="Describe the e-commerce content you want to create..."
                    type="text"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
                  />
                  <button
                    onClick={() => handleGenerate()}
                    disabled={isGenerating || !prompt.trim()}
                    className="bg-primary hover:bg-secondary text-white font-semibold px-6 py-2.5 rounded-xl flex items-center gap-2 transition-colors shadow-lg active:scale-95 disabled:opacity-50"
                  >
                    <span className="material-icons-round text-sm">auto_awesome</span>
                    {isGenerating ? 'Wait...' : 'Generate'}
                  </button>
                </div>

                {uploadedImage && (
                  <div className="mt-4 animate-fade-in-up flex items-center gap-4 bg-white/50 dark:bg-surface-dark/50 backdrop-blur rounded-xl p-3 border border-slate-100 dark:border-slate-700">
                    <img src={uploadedImage} alt="Uploaded preview" className="h-16 w-16 object-cover rounded-lg shadow-sm" />
                    <div className="flex-1">
                      <p className="text-xs font-bold text-slate-800 dark:text-slate-200">Image Uploaded</p>
                      <p className="text-[10px] text-slate-500">Ready for generation context</p>
                    </div>
                    <button onClick={() => setUploadedImage(null)} className="p-1 hover:bg-red-50 dark:hover:bg-red-900/20 text-slate-400 hover:text-red-500 rounded-lg transition-all">
                      <span className="material-icons-round text-sm">close</span>
                    </button>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl mb-12 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                <button
                  onClick={() => handleNavigateToChat("Create a luxurious and captivating product description for this 'Midnight Suede' perfume, focusing on its base notes of sandalwood and musk.", GenerationType.TEXT, "https://images.unsplash.com/photo-1594035910387-fea47794261f?q=80&w=600&auto=format&fit=crop")}
                  className="group flex flex-col text-left bg-white dark:bg-surface-dark border border-slate-100 dark:border-slate-700 hover:border-primary rounded-2xl p-4 shadow-sm hover:shadow-glow transition-all duration-300 transform hover:-translate-y-1 overflow-hidden h-full"
                >
                  <div className="h-32 w-full bg-slate-50 dark:bg-slate-800 rounded-xl mb-4 overflow-hidden relative border border-slate-100 dark:border-slate-700">
                    <img alt="Luxury Perfume" className="w-full h-full object-cover opacity-90 group-hover:scale-105 transition-transform duration-700" src="https://images.unsplash.com/photo-1594035910387-fea47794261f?q=80&w=600&auto=format&fit=crop" />
                  </div>
                  <div className="flex items-center gap-2 mb-1">
                    <div className="p-1.5 rounded-lg bg-orange-50 text-orange-500 dark:bg-orange-500/10">
                      <span className="material-icons-round text-xl">description</span>
                    </div>
                    <h3 className="font-bold text-slate-900 dark:text-white group-hover:text-primary transition-colors">Product Copy</h3>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">High-converting copy for premium e-commerce markets.</p>
                </button>

                <button
                  onClick={() => handleNavigateToChat("Generate a set of 4 professional studio listing images for these red performance sneakers, including a 45-degree angle and a sole detail shot.", GenerationType.IMAGE, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600&auto=format&fit=crop")}
                  className="group flex flex-col text-left bg-white dark:bg-surface-dark border border-slate-100 dark:border-slate-700 hover:border-primary rounded-2xl p-4 shadow-sm hover:shadow-glow transition-all duration-300 transform hover:-translate-y-1 overflow-hidden h-full"
                >
                  <div className="h-32 w-full bg-slate-50 dark:bg-slate-800 rounded-xl mb-4 overflow-hidden relative border border-slate-100 dark:border-slate-700">
                    <img alt="Sport Sneaker" className="w-full h-full object-cover opacity-90 group-hover:scale-105 transition-transform duration-700" src="https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600&auto=format&fit=crop" />
                  </div>
                  <div className="flex items-center gap-2 mb-1">
                    <div className="p-1.5 rounded-lg bg-blue-50 text-blue-500 dark:bg-blue-500/10">
                      <span className="material-icons-round text-xl">image</span>
                    </div>
                    <h3 className="font-bold text-slate-900 dark:text-white group-hover:text-primary transition-colors">Listing Images</h3>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">Studio-quality photography rendered by specialized AI.</p>
                </button>

                <button
                  onClick={() => handleNavigateToChat("Produce a high-energy 15-second social media video ad for this smartwatch, highlighting its fitness tracking features and sleek AMOLED display.", GenerationType.VIDEO, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=600&auto=format&fit=crop")}
                  className="group flex flex-col text-left bg-white dark:bg-surface-dark border border-slate-100 dark:border-slate-700 hover:border-primary rounded-2xl p-4 shadow-sm hover:shadow-glow transition-all duration-300 transform hover:-translate-y-1 overflow-hidden h-full"
                >
                  <div className="h-32 w-full bg-slate-50 dark:bg-slate-800 rounded-xl mb-4 overflow-hidden relative border border-slate-100 dark:border-slate-700">
                    <img alt="Modern Smartwatch" className="w-full h-full object-cover opacity-90 group-hover:scale-105 transition-transform duration-700" src="https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=600&auto=format&fit=crop" />
                  </div>
                  <div className="flex items-center gap-2 mb-1">
                    <div className="p-1.5 rounded-lg bg-pink-50 text-pink-500 dark:bg-pink-500/10">
                      <span className="material-icons-round text-xl">videocam</span>
                    </div>
                    <h3 className="font-bold text-slate-900 dark:text-white group-hover:text-primary transition-colors">Ad Video</h3>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">Dynamic video ads ready for social platform sharing.</p>
                </button>
              </div>
            </div>
          </div>
        )}

        {currentView === 'chat' && (
          <div className="flex-1 flex flex-col h-full bg-white dark:bg-background-dark animate-fade-in">
            {/* Chat Header */}
            <div className="flex items-center justify-between px-8 py-4 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2 text-slate-400 text-sm">
                <span className="hover:text-primary cursor-pointer transition-colors" onClick={() => navigateTo('home')}>Dashboard</span>
                <span className="material-icons-round text-[14px]">chevron_right</span>
                <span className="text-slate-800 dark:text-slate-200 font-bold">New Dialogue</span>
              </div>
              <div className="flex items-center gap-4">
                <button onClick={() => setDarkMode(!darkMode)} className="p-2 rounded-full text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                  <span className="material-icons-round">{darkMode ? 'light_mode' : 'dark_mode'}</span>
                </button>
                <button
                  onClick={() => setIsNotificationModalOpen(true)}
                  className="p-2 rounded-full text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors relative"
                >
                  <span className="material-symbols-outlined">notifications</span>
                  <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full"></span>
                </button>
                <button className="p-2 rounded-full text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                  <span className="material-symbols-outlined">more_vert</span>
                </button>
              </div>
            </div>

            {/* Chat Messages */}
            <div ref={chatScrollRef} className="flex-1 overflow-y-auto sidebar-scroll px-4 md:px-12 py-8 space-y-8 scroll-smooth">
              <div className="max-w-4xl mx-auto flex flex-col gap-8">
                <div className="flex justify-center">
                  <span className="text-xs font-bold text-slate-400 dark:text-slate-600 uppercase tracking-widest bg-slate-50 dark:bg-slate-800/50 px-3 py-1 rounded-full">Today, {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>

                {userMessage && (
                  <div className="flex justify-end w-full group animate-fade-in-up">
                    <div className="flex flex-col items-end max-w-[80%] md:max-w-[70%] gap-2">
                      <div className="flex flex-col gap-2">
                        <div className="bg-slate-100 dark:bg-[#1f2e2d] text-slate-800 dark:text-slate-100 px-5 py-3.5 rounded-2xl rounded-tr-sm text-[15px] leading-relaxed shadow-sm">
                          {userMessage}
                        </div>
                        {sentUserImage && (
                          <div className="rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 shadow-sm max-w-sm animate-fade-in-up self-end">
                            <img src={sentUserImage} alt="User Context" className="w-full h-auto object-cover max-h-64" />
                          </div>
                        )}
                      </div>
                      <span className="text-[11px] text-slate-400 font-bold pr-1 uppercase tracking-widest">YOU</span>
                    </div>
                  </div>
                )}

                {(result || isGenerating) && (
                  <div className="flex justify-start w-full animate-fade-in-up">
                    <div className="flex-1 max-w-[85%] md:max-w-[80%]">
                      <GeminiResult
                        isGenerating={isGenerating}
                        pendingType={activeGenerationType}
                        result={result}
                        userMessage={null}
                        onReset={() => handleGenerate(activeGenerationType || GenerationType.TEXT, userMessage || "")}
                        onImageClick={(content) => openAssetDetail({ title: 'Generated Asset', url: content, type: result?.type === GenerationType.VIDEO ? 'video' : 'image' })}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Input Bar */}
            <div className="p-4 md:p-6 pb-8 border-t border-slate-100 dark:border-slate-800">
              <div className="max-w-3xl mx-auto">
                <div className="relative flex flex-col w-full bg-white dark:bg-[#1f2e2d] border border-slate-200 dark:border-slate-700 rounded-2xl shadow-sm hover:shadow-md focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all duration-200 overflow-hidden">
                  <textarea
                    className="w-full bg-transparent border-none text-slate-800 dark:text-slate-100 placeholder-slate-400 px-5 py-4 min-h-[60px] max-h-[200px] resize-none focus:ring-0 text-base leading-relaxed"
                    placeholder="Ask for variations or new content..."
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleGenerate(activeGenerationType || GenerationType.TEXT);
                      }
                    }}
                  ></textarea>
                  <div className="flex items-center justify-between px-3 py-2 bg-slate-50 dark:bg-[#1a2625] border-t border-slate-100 dark:border-slate-700">
                    <div className="flex items-center gap-1">
                      <button className="p-2 rounded-lg text-slate-500 hover:text-primary hover:bg-white dark:hover:bg-slate-800 transition-all"><span className="material-symbols-outlined text-[20px]">attach_file</span></button>
                      <button onClick={handleImageIconClick} className="p-2 rounded-lg text-slate-500 hover:text-primary hover:bg-white dark:hover:bg-slate-800 transition-all"><span className="material-symbols-outlined text-[20px]">image</span></button>
                      <button className="p-2 rounded-lg text-slate-500 hover:text-primary hover:bg-white dark:hover:bg-slate-800 transition-all"><span className="material-symbols-outlined text-[20px]">videocam</span></button>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-[10px] text-slate-400 font-bold hidden sm:block">SHIFT + ENTER FOR NEW LINE</span>
                      <button
                        onClick={() => handleGenerate(activeGenerationType || GenerationType.TEXT)}
                        disabled={isGenerating || !prompt.trim()}
                        className="flex items-center justify-center w-10 h-10 rounded-xl bg-primary hover:bg-primary-hover text-slate-900 shadow-sm transition-colors transform active:scale-95 disabled:opacity-50"
                      >
                        <span className="material-symbols-outlined text-[20px] ml-0.5">send</span>
                      </button>
                    </div>
                  </div>
                </div>
                <div className="text-center mt-3">
                  <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">AI Content Generation • Specialized Commerce Models</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentView === 'gallery' && <Gallery onGenerateNew={() => navigateTo('home')} onAssetClick={openAssetDetail} />}
        {currentView === 'projects' && <Projects onNewProject={() => navigateTo('home')} onAssetClick={openAssetDetail} />}
        {currentView === 'insights' && <Insights />}
        {currentView === 'settings' && <Settings />}
        {currentView === 'help-support' && <HelpSupport />}
        {currentView === 'asset-detail' && <AssetDetail asset={selectedAsset} onBack={() => navigateTo('projects')} onAssetClick={openAssetDetail} />}
        {currentView === 'video-detail' && <VideoDetail video={selectedAsset} onClose={() => navigateTo('gallery')} />}
        {currentView === 'image-detail' && <ImageDetail image={selectedAsset} onClose={() => navigateTo('gallery')} />}
        {currentView === 'project-timeline' && <ProjectTimeline project={selectedAsset} onBack={() => navigateTo('projects')} />}
      </main>

      {isPricingModalOpen && <PricingModal onClose={() => setIsPricingModalOpen(false)} />}
      {isUserProfileModalOpen && <UserProfileModal onClose={() => setIsUserProfileModalOpen(false)} />}
      {isNotificationModalOpen && <NotificationModal onClose={() => setIsNotificationModalOpen(false)} />}
    </div>
  );
};

export default App;
