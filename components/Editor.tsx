
import React, { useState } from 'react';

interface EditorProps {
  darkMode: boolean;
  onToggleDarkMode: () => void;
  onAssetClick?: (asset: any) => void;
}

const Editor: React.FC<EditorProps> = ({ darkMode, onToggleDarkMode, onAssetClick }) => {
  const [activeTab, setActiveTab] = useState<'copy' | 'images' | 'video'>('copy');

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden bg-background-light dark:bg-background-dark">
      {/* Internal Header */}
      <header className="h-16 bg-surface-light dark:bg-surface-dark border-b border-border-light dark:border-border-dark flex items-center justify-between px-6 flex-shrink-0 z-10 transition-colors">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-slate-400 dark:text-slate-500">
            <span>Workspace</span>
            <span className="material-icons-round text-base">chevron_right</span>
            <span className="text-slate-900 dark:text-white font-medium">Summer Campaign 2024</span>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="hidden md:flex items-center bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button className="px-3 py-1 bg-white dark:bg-gray-700 shadow-sm rounded-md text-xs font-medium text-slate-900 dark:text-white">Design</button>
            <button className="px-3 py-1 text-xs font-medium text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">Code</button>
          </div>
          <button className="text-slate-400 dark:text-slate-500 hover:bg-gray-100 dark:hover:bg-gray-800 p-2 rounded-full transition-colors">
            <span className="material-icons-round">notifications_none</span>
          </button>
          <button 
            onClick={onToggleDarkMode}
            className="text-slate-400 dark:text-slate-500 hover:bg-gray-100 dark:hover:bg-gray-800 p-2 rounded-full transition-colors"
          >
            <span className="material-icons-round">{darkMode ? 'light_mode' : 'dark_mode'}</span>
          </button>
          <button className="bg-primary hover:bg-secondary text-white px-4 py-2 rounded-lg text-sm font-medium shadow-md shadow-teal-500/20 transition-colors flex items-center">
            <span className="material-icons-round text-sm mr-2">ios_share</span> Export
          </button>
        </div>
      </header>

      <div className="flex-1 overflow-hidden flex flex-col md:flex-row bg-gray-50 dark:bg-gray-900/50">
        {/* Left Sidebar: Source Product */}
        <div className="w-full md:w-1/3 xl:w-1/4 p-6 border-r border-border-light dark:border-border-dark overflow-y-auto bg-surface-light dark:bg-surface-dark transition-colors">
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-1 text-slate-900 dark:text-white">Source Product</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">The base image for all generations.</p>
          </div>
          <div 
            onClick={() => onAssetClick?.({ title: 'Nike Air Max Red', type: 'image', url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBA6W_bdhwyeJqUpYJkmJlVjsowZdbWB_oJeJcwjB28z4Bs8qxelX7SZIlg4zfOmrTtAtjicwpLE_z-N-2mAj0fLg3ANis61sKlmmIWKZIw33c_z9k6CfhxfNqYx8eY3OqT7tXUlpD6SNiRMbYLL3pFLmve98_th73HCuK-oWAg-sBf83kyQ4YA8Z9Biv316EFFExHcsIsyhZRZOjap9fO6Mwfd1gWL_b-J7Vix_L_men7ueQBDyaOxJyQSmeUhUtfie0SiWF7bcP8' })}
            className="relative group rounded-2xl overflow-hidden shadow-lg border border-border-light dark:border-border-dark bg-gray-100 dark:bg-gray-800 aspect-square mb-6 cursor-pointer"
          >
            <img 
              alt="Red Nike Running Shoe" 
              className="w-full h-full object-cover p-4 hover:scale-105 transition-transform duration-500" 
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuBA6W_bdhwyeJqUpYJkmJlVjsowZdbWB_oJeJcwjB28z4Bs8qxelX7SZIlg4zfOmrTtAtjicwpLE_z-N-2mAj0fLg3ANis61sKlmmIWKZIw33c_z9k6CfhxfNqYx8eY3OqT7tXUlpD6SNiRMbYLL3pFLmve98_th73HCuK-oWAg-sBf83kyQ4YA8Z9Biv316EFFExHcsIsyhZRZOjap9fO6Mwfd1gWL_b-J7Vix_L_men7ueQBDyaOxJyQSmeUhUtfie0SiWF7bcP8"
            />
            <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
              <button className="bg-black/50 hover:bg-black/70 text-white p-2 rounded-full backdrop-blur-sm">
                <span className="material-icons-round text-sm">edit</span>
              </button>
            </div>
          </div>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-700 dark:text-slate-300">Product Name</label>
              <input 
                className="w-full bg-gray-50 dark:bg-gray-800 border-border-light dark:border-border-dark rounded-lg text-sm px-3 py-2.5 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white shadow-sm" 
                type="text" 
                defaultValue="Nike Air Max Red"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-700 dark:text-slate-300">Brand Voice</label>
              <select className="w-full bg-gray-50 dark:bg-gray-800 border-border-light dark:border-border-dark rounded-lg text-sm px-3 py-2.5 focus:ring-2 focus:ring-primary focus:border-transparent outline-none text-slate-900 dark:text-white shadow-sm">
                <option>Energetic & Bold</option>
                <option>Minimalist</option>
                <option>Professional</option>
                <option>Luxury</option>
              </select>
            </div>
            <div className="pt-4 border-t border-border-light dark:border-border-dark">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">Detection Tags</h3>
                <button className="text-primary hover:text-secondary text-xs hover:underline">Edit</button>
              </div>
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-1 bg-teal-50 dark:bg-teal-900/30 text-teal-700 dark:text-teal-300 rounded-md text-xs font-medium border border-teal-100 dark:border-teal-800">Footwear</span>
                <span className="px-2 py-1 bg-teal-50 dark:bg-teal-900/30 text-teal-700 dark:text-teal-300 rounded-md text-xs font-medium border border-teal-100 dark:border-teal-800">Red</span>
                <span className="px-2 py-1 bg-teal-50 dark:bg-teal-900/30 text-teal-700 dark:text-teal-300 rounded-md text-xs font-medium border border-teal-100 dark:border-teal-800">Sport</span>
                <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-slate-500 dark:text-slate-400 rounded-md text-xs font-medium border border-border-light dark:border-border-dark cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700">+ Add</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Workspace Area */}
        <div className="flex-1 flex flex-col min-w-0 bg-background-light dark:bg-background-dark relative transition-colors">
          <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-8 scroll-smooth pb-32 sidebar-scroll">
            {/* User Message */}
            <div className="flex justify-end animate-fade-in-up">
              <div className="flex items-end max-w-2xl">
                <div className="bg-primary text-white p-4 rounded-2xl rounded-br-none shadow-md">
                  <p className="text-sm leading-relaxed">Generate a summer sale campaign package for this shoe. I need catchy Instagram captions, lifestyle images in a city park setting, and a short 15s video teaser.</p>
                </div>
                <img 
                  alt="User" 
                  className="w-8 h-8 rounded-full ml-3 border border-border-light dark:border-gray-700" 
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuBLn-3O5FJyYjgoDB5R6sS8IJXm3DoFegg_gXC3d02sSQK61KFRwytqwZ8ILIJc_WWqLGJqZN7G7eEEU0EsY1G-N66i3jlYFAB7sosq020OMtxwJP227a2MD-TCsR179t1hTHdtiVo2OE31J_kwOejJLTjbH163Klhl_C41-Ljr2InHVH7mErL1XljUWzqCkHfBmfX7Upjgf3c6u1_X87JrY3ARrG-1Wl9_7vaZLfPlZRxAtlDElxkXWpSGfgZT12bIiiLwWvIg3xU"
                />
              </div>
            </div>

            {/* AI Response */}
            <div className="flex items-start max-w-5xl animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-teal-400 to-cyan-500 flex-shrink-0 flex items-center justify-center text-white mr-4 mt-1 shadow-lg shadow-teal-500/20">
                <span className="material-icons-round text-sm">smart_toy</span>
              </div>
              <div className="flex-1 space-y-6">
                <div className="bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark p-6 rounded-2xl rounded-tl-none shadow-sm transition-colors">
                  <p className="text-sm text-slate-900 dark:text-white mb-4 font-inter">I've generated a complete campaign package based on "Energetic & Bold" style. Here are the results separated by media type:</p>
                  
                  {/* Tabs */}
                  <div className="border-b border-border-light dark:border-border-dark mb-6">
                    <nav aria-label="Tabs" className="-mb-px flex space-x-8">
                      <button 
                        onClick={() => setActiveTab('copy')}
                        className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-all ${
                          activeTab === 'copy' 
                          ? 'border-primary text-primary' 
                          : 'border-transparent text-slate-400 dark:text-slate-500 hover:text-slate-900 dark:hover:text-white hover:border-gray-300'
                        }`}
                      >
                        <span className="material-icons-round text-lg mr-2">description</span> Copy
                      </button>
                      <button 
                        onClick={() => setActiveTab('images')}
                        className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-all ${
                          activeTab === 'images' 
                          ? 'border-primary text-primary' 
                          : 'border-transparent text-slate-400 dark:text-slate-500 hover:text-slate-900 dark:hover:text-white hover:border-gray-300'
                        }`}
                      >
                        <span className="material-icons-round text-lg mr-2">image</span> Images
                        <span className="ml-2 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 py-0.5 px-2 rounded-full text-xs">4</span>
                      </button>
                      <button 
                        onClick={() => setActiveTab('video')}
                        className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-all ${
                          activeTab === 'video' 
                          ? 'border-primary text-primary' 
                          : 'border-transparent text-slate-400 dark:text-slate-500 hover:text-slate-900 dark:hover:text-white hover:border-gray-300'
                        }`}
                      >
                        <span className="material-icons-round text-lg mr-2">movie</span> Video
                      </button>
                    </nav>
                  </div>

                  {/* Tab Content */}
                  <div className="space-y-4">
                    {activeTab === 'copy' && (
                      <>
                        <div className="group relative bg-gray-50 dark:bg-gray-900/50 p-4 rounded-xl border border-dashed border-border-light dark:border-border-dark hover:border-primary/50 transition-colors">
                          <div className="flex justify-between items-start mb-2">
                            <span className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Instagram Caption 1</span>
                            <div className="flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                              <button className="text-slate-400 dark:text-slate-500 hover:text-primary"><span className="material-icons-round text-sm">content_copy</span></button>
                              <button className="text-slate-400 dark:text-slate-500 hover:text-primary"><span className="material-icons-round text-sm">refresh</span></button>
                            </div>
                          </div>
                          <p className="text-sm text-slate-900 dark:text-white leading-relaxed font-inter">
                            Step up your game this summer with the new Air Max Red. 🔴🔥 Designed for the bold, built for the streets. #RunTheCity #SummerVibes #SneakerHead
                          </p>
                        </div>
                        <div className="group relative bg-gray-50 dark:bg-gray-900/50 p-4 rounded-xl border border-dashed border-border-light dark:border-border-dark hover:border-primary/50 transition-colors">
                          <div className="flex justify-between items-start mb-2">
                            <span className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Facebook Ad Headline</span>
                            <div className="flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                              <button className="text-slate-400 dark:text-slate-500 hover:text-primary"><span className="material-icons-round text-sm">content_copy</span></button>
                              <button className="text-slate-400 dark:text-slate-500 hover:text-primary"><span className="material-icons-round text-sm">refresh</span></button>
                            </div>
                          </div>
                          <p className="text-sm text-slate-900 dark:text-white leading-relaxed font-medium font-inter">
                            Flash Sale: 20% Off The Season's Hottest Kicks. Limited Time Only.
                          </p>
                        </div>
                      </>
                    )}
                    {activeTab === 'images' && (
                      <div className="grid grid-cols-2 gap-4">
                        {[
                          "https://lh3.googleusercontent.com/aida-public/AB6AXuA9eETmbEtytEvCDU1elZvp8DzU9tsXCQETcPlYv-uyyENK5ViJ421p8yx3D7QDvu5Tg6fuicI6-Fc5RtcOp-ZNbfuNSia87MX-3zN-t_qhTnVCYDkWlcd5PvCwNRKS7VMM72kimmVqxVZKNss7epry-QhYtY1sku0HwfTqKo8d-na25aD3orE-uL7GY_4SP0HzmOXpmyZfaJNIFAn_xStSFAGR5vHMx21d4O0r35TzjNTwzLM_BfyfADbwcP7LgP7pH-zHS9DheCY",
                          "https://lh3.googleusercontent.com/aida-public/AB6AXuCrePcJJlCbpRtCy3YLzhWcbe5lEgmjTTRBGRsfjyqonTk_C1r8Kj7tsMOiEiFO1kYNhVgpo5NiKkghK6SVHrm8REU_d2qLhhw3GvmnZSkA-Ep0dOxU56wYDx-lJFwOIn2aIn3Mb4KnGyEr19NVMgj7lRmOvIqv9uvHSWH6IdiumZSrG_eT6Wz_YMhEe27wMdcaCo5QZeS3x5GF-Cpyc9wD-fpoJ40i7AUwS1DWSv8uj7waaSqK5KnGLhlhl04ZgcbyNAmfzL8IeYY"
                        ].map((url, i) => (
                          <div 
                            key={i} 
                            onClick={() => onAssetClick?.({ title: `Generated V${i+1}`, type: 'image', url })}
                            className="relative group rounded-xl overflow-hidden aspect-[4/3] cursor-pointer shadow-sm"
                          >
                            <img alt={`Result ${i}`} className="w-full h-full object-cover hover:scale-105 transition-transform duration-500" src={url} />
                            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                              <span className="bg-white/90 dark:bg-black/80 text-slate-900 dark:text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0 transition-all shadow-lg">
                                <span className="material-icons-round text-lg">visibility</span>
                              </span>
                            </div>
                            <span className="absolute top-2 left-2 bg-black/60 backdrop-blur-md text-white text-[10px] px-2 py-0.5 rounded">V{i+1}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    {activeTab === 'video' && (
                      <div className="relative aspect-video rounded-xl overflow-hidden bg-slate-900 flex items-center justify-center">
                        <span className="material-icons-round text-4xl text-white/50">play_circle_outline</span>
                        <p className="absolute bottom-4 left-4 text-xs text-white/70">Video placeholder (15s Teaser)</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Footer Actions */}
                <div className="flex items-center space-x-3 pl-2">
                  <button className="text-slate-400 dark:text-slate-500 hover:text-primary flex items-center text-sm transition-colors">
                    <span className="material-icons-round text-base mr-1">thumb_up</span> Helpful
                  </button>
                  <button className="text-slate-400 dark:text-slate-500 hover:text-red-500 flex items-center text-sm transition-colors">
                    <span className="material-icons-round text-base mr-1">thumb_down</span> Bad result
                  </button>
                  <div className="flex-1"></div>
                  <button className="text-slate-400 dark:text-slate-500 hover:text-primary flex items-center text-sm transition-colors">
                    <span className="material-icons-round text-base mr-1">history</span> View history
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Floating Input Bar */}
          <div className="absolute bottom-0 left-0 right-0 bg-surface-light dark:bg-surface-dark border-t border-border-light dark:border-border-dark p-4 md:p-6 z-20 transition-colors">
            <div className="max-w-4xl mx-auto relative">
              {/* Pill Suggestions */}
              <div className="absolute -top-12 left-0 flex space-x-2 overflow-x-auto w-full pb-2 no-scrollbar">
                {[
                  { icon: 'bolt', color: 'text-yellow-500', label: 'Regenerate Images' },
                  { icon: 'edit', color: 'text-blue-500', label: 'Shorten Copy' },
                  { icon: 'translate', color: 'text-green-500', label: 'Translate to Spanish' }
                ].map((pill, i) => (
                  <button key={i} className="flex items-center space-x-1.5 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark px-3 py-1.5 rounded-full text-xs font-medium shadow-sm hover:border-primary dark:hover:border-primary transition-colors text-slate-700 dark:text-white whitespace-nowrap">
                    <span className={`material-icons-round text-sm ${pill.color}`}>{pill.icon}</span>
                    <span>{pill.label}</span>
                  </button>
                ))}
              </div>
              
              {/* Input Field Container */}
              <div className="relative bg-gray-50 dark:bg-gray-900 border border-border-light dark:border-border-dark rounded-2xl shadow-sm focus-within:ring-2 focus-within:ring-primary focus-within:border-transparent transition-all">
                <div className="flex items-center px-4 py-3">
                  <button className="text-slate-400 dark:text-slate-500 hover:text-primary transition-colors p-1">
                    <span className="material-icons-round">add_circle_outline</span>
                  </button>
                  <input 
                    className="flex-1 bg-transparent border-none focus:ring-0 text-sm text-slate-900 dark:text-white placeholder-slate-400 mx-2" 
                    placeholder="Refine the copy or request more variations..." 
                    type="text"
                  />
                  <button className="text-slate-400 dark:text-slate-500 hover:text-primary transition-colors p-1">
                    <span className="material-icons-round">mic</span>
                  </button>
                  <button className="bg-primary hover:bg-secondary text-white rounded-xl p-2 ml-2 shadow-md transition-all active:scale-95">
                    <span className="material-icons-round text-xl">arrow_upward</span>
                  </button>
                </div>
              </div>
              <p className="text-center text-[10px] text-slate-400 dark:text-slate-500 mt-2">
                CommerceAI can make mistakes. Please review generated content.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Editor;
