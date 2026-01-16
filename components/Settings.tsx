
import React, { useState } from 'react';

type SettingsTab = 'profile' | 'account' | 'billing' | 'ai-preferences' | 'integrations';

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<SettingsTab>('ai-preferences');
  const [language, setLanguage] = useState('English (US)');
  const [tone, setTone] = useState('Luxury & Sophisticated');
  const [aspectRatio, setAspectRatio] = useState('square');
  const [integrations, setIntegrations] = useState({
    shopify: true,
    amazon: false,
    tiktok: true
  });

  const handleAction = (label: string) => {
    alert(`Action: ${label}`);
  };

  const handleSave = () => {
    alert("Settings saved successfully!");
  };

  const toggleIntegration = (platform: keyof typeof integrations) => {
    setIntegrations(prev => ({ ...prev, [platform]: !prev[platform] }));
  };

  return (
    <div className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark transition-colors">
      <div className="w-full max-w-[1200px] mx-auto p-6 md:p-10 lg:p-14">
        <div className="flex flex-col gap-2 mb-10 animate-fade-in-up">
          <h2 className="text-3xl md:text-4xl font-black tracking-tight text-text-main dark:text-white">System Settings</h2>
          <p className="text-text-muted dark:text-gray-400 text-lg">Manage your global AI preferences, integrations, and account configurations.</p>
        </div>

        <div className="flex flex-col md:flex-row gap-8 items-start">
          {/* Inner Navigation */}
          <div className="w-full md:w-64 flex-shrink-0 flex flex-col gap-1 sticky top-0 animate-fade-in-up">
            {[
              { id: 'profile', label: 'Profile' },
              { id: 'account', label: 'Account & Security' },
              { id: 'billing', label: 'Billing & Subscription' },
              { id: 'ai-preferences', label: 'AI Preferences', showChevron: true },
              { id: 'integrations', label: 'Integrations' },
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id as SettingsTab)}
                className={`flex items-center justify-between px-4 py-3 text-sm font-medium transition-all rounded-lg group ${
                  activeTab === item.id 
                  ? 'text-text-main dark:text-white bg-white dark:bg-[#1d2928] shadow-sm border-l-4 border-primary font-bold' 
                  : 'text-text-muted hover:text-text-main hover:bg-white dark:hover:bg-gray-800'
                }`}
              >
                {item.label}
                {item.showChevron && <span className="material-symbols-outlined text-primary text-[18px]">chevron_right</span>}
              </button>
            ))}
          </div>

          {/* Main Content Area */}
          <div className="flex-1 w-full flex flex-col gap-8 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            
            {/* AI Preferences Panel */}
            {activeTab === 'ai-preferences' && (
              <div className="bg-white dark:bg-[#1d2928] rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-6 md:p-8 transition-colors">
                <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-100 dark:border-gray-800">
                  <span className="p-2 bg-primary/20 rounded-lg text-primary-dark dark:text-primary material-symbols-outlined">tune</span>
                  <h3 className="text-xl font-bold text-text-main dark:text-white">Global Configuration</h3>
                </div>
                
                <form className="flex flex-col gap-8" onSubmit={(e) => e.preventDefault()}>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-8 items-start">
                    <div className="md:col-span-1">
                      <label className="text-sm font-bold text-text-main dark:text-gray-200">Default Language</label>
                      <p className="text-xs text-text-muted mt-1">Select the primary language for AI generated content.</p>
                    </div>
                    <div className="md:col-span-2 relative">
                      <select 
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 text-text-main dark:text-gray-200 rounded-lg h-12 px-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none appearance-none cursor-pointer"
                      >
                        <option>English (US)</option>
                        <option>English (UK)</option>
                        <option>Spanish</option>
                        <option>French</option>
                        <option>German</option>
                      </select>
                      <span className="material-symbols-outlined absolute right-4 top-3 text-gray-400 pointer-events-none">expand_more</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-8 items-start">
                    <div className="md:col-span-1">
                      <label className="text-sm font-bold text-text-main dark:text-gray-200">Brand Tone of Voice</label>
                      <p className="text-xs text-text-muted mt-1">Define how your brand sounds to customers.</p>
                    </div>
                    <div className="md:col-span-2 relative">
                      <div className="flex flex-col gap-3">
                        <select 
                          value={tone}
                          onChange={(e) => setTone(e.target.value)}
                          className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 text-text-main dark:text-gray-200 rounded-lg h-12 px-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none appearance-none cursor-pointer"
                        >
                          <option>Luxury & Sophisticated</option>
                          <option>Professional & Trustworthy</option>
                          <option>Friendly & Approachable</option>
                          <option>Witty & Playful</option>
                        </select>
                        <span className="material-symbols-outlined absolute right-4 top-3 text-gray-400 pointer-events-none">expand_more</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          <span className="px-3 py-1 rounded-full bg-primary/10 text-primary-dark text-xs font-semibold border border-primary/20">Elegant</span>
                          <span className="px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500 text-xs font-medium border border-gray-200 dark:border-gray-700">Minimalist</span>
                          <span className="px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500 text-xs font-medium border border-gray-200 dark:border-gray-700">Premium</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-8 items-start">
                    <div className="md:col-span-1">
                      <label className="text-sm font-bold text-text-main dark:text-gray-200">Image Settings</label>
                      <p className="text-xs text-text-muted mt-1">Set the default aspect ratio for generated product images.</p>
                    </div>
                    <div className="md:col-span-2">
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                        {[
                          { id: 'square', label: 'Square', meta: '1024x1024', iconSize: 'w-8 h-8' },
                          { id: 'landscape', label: 'Landscape', meta: '16:9', iconSize: 'w-10 h-6' },
                          { id: 'portrait', label: 'Portrait', meta: '9:16', iconSize: 'w-6 h-10' },
                        ].map((ratio) => (
                          <label key={ratio.id} className="cursor-pointer group">
                            <input 
                              type="radio" 
                              className="peer sr-only" 
                              name="resolution" 
                              checked={aspectRatio === ratio.id}
                              onChange={() => setAspectRatio(ratio.id)}
                            />
                            <div className="flex flex-col items-center justify-center p-4 rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-background-light dark:bg-background-dark peer-checked:border-primary peer-checked:bg-primary/5 transition-all">
                              <div className={`${ratio.iconSize} rounded border-2 border-current mb-2 opacity-40 group-hover:opacity-100 text-primary-dark dark:text-primary transition-opacity`}></div>
                              <span className="text-sm font-bold text-text-main dark:text-white">{ratio.label}</span>
                              <span className="text-[10px] text-text-muted">{ratio.meta}</span>
                            </div>
                          </label>
                        ))}
                      </div>
                    </div>
                  </div>
                </form>
              </div>
            )}

            {/* Integrations Panel */}
            <div className="bg-white dark:bg-[#1d2928] rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-6 md:p-8" id="integrations">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-100 dark:border-gray-800">
                <div className="flex items-center gap-3">
                  <span className="p-2 bg-primary/20 rounded-lg text-primary-dark dark:text-primary material-symbols-outlined">extension</span>
                  <h3 className="text-xl font-bold text-text-main dark:text-white">Integrations</h3>
                </div>
                <button 
                  onClick={() => handleAction('View All Integrations')}
                  className="text-sm font-semibold text-primary-dark hover:text-primary transition-colors"
                >
                  View All
                </button>
              </div>
              <div className="flex flex-col gap-4">
                {/* Integration items */}
                {[
                  { id: 'shopify', name: 'Shopify', desc: 'Sync products & update images', logo: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCg5dVXuGtTH18rTJy4sPob1Apf8OkFIppFdPBKyuGODBnp3Yxwxa5admUobQAiSuemnYwcjI8CixBuZ-QTBlbuUpRJ7ZAQ9sweta1xnNtO5_vgLdTzqZp-6qzntghxIiqo5RzKTF60rdCUKmwPWw8nKdSZ3UdfTiRGBY76RAy62LGJ5rS2AG6KPLDFMa6mMbDjgwb9nxg5Cg_2ALgOCpwSyiBh-cnDkVFpKiO0T8mWIbAT4GHbGJzIs4JVfZg7nUVMzw-dwUACSrA' },
                  { id: 'amazon', name: 'Amazon', desc: 'A+ Content generation', logo: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAZ32FhLUnQZsHOrwMD_3GJy3FYHB1yEtPqG3GGiWGl0KglL1xEDthI0XKLf6l3tp6fKY5J_5b6sC8xXgPcUSwbXJ8fs2WupX4rWZOMQwGKNBZAQ2s_hFbnMRUIt1uBnMA2qk-9DRApbBkBBhp1rhswUfJ1f6dCaPE0o5eii7bJOuB23S_FFs32lyIiqGhQSbVz4vIkNwt8iM0wu1RvyFBFQDuUrjoNkC-7MU6Be2uocfkfhmrlpQLn8e4fEaA2fvk6JqK3k6f_mUk' },
                  { id: 'tiktok', name: 'TikTok Shop', desc: 'Video ad generation', logo: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCy06PLy7yp9gdBtu5PuQZGOsWHIxRk_49oNrgWUxgo6VOnWUceE2zV4I6g2l-0yOgxu91rIYCZ9q_N_XxNsTCBhkqn3xRy39Tv-qBnlF2g6XTO-bXlugWX6aDBTK9vT-IBwxit8mfViTqtYAWrXxSS5ahdcB8BMF0RXfCxS0AL58KbIA42E6T8_TeYtSLctelnqZFDWXlWoQ5eetuzoO55wVENfb7gwdrDOsdnuy15mM3VzH-G5XyHZV1DfRdYbUcLpV-TZxsMcWI' }
                ].map((item) => (
                  <div key={item.id} className="flex items-center justify-between p-4 rounded-lg bg-background-light dark:bg-background-dark border border-gray-100 dark:border-gray-700 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="bg-white p-2 rounded-lg shadow-sm border border-gray-100 w-12 h-12 flex items-center justify-center">
                        <img alt={item.name} className={`w-8 h-8 object-contain ${item.id === 'tiktok' ? 'bg-black p-1 rounded filter invert' : ''}`} src={item.logo} />
                      </div>
                      <div>
                        <h4 className="text-base font-bold text-text-main dark:text-white">{item.name}</h4>
                        <p className="text-xs text-text-muted">{item.desc}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`text-xs font-medium px-2 py-1 rounded transition-colors ${
                        integrations[item.id as keyof typeof integrations] 
                        ? 'text-green-600 bg-green-100 dark:bg-green-900/30 dark:text-green-400' 
                        : 'text-gray-500 bg-gray-100 dark:bg-gray-800'
                      }`}>
                        {integrations[item.id as keyof typeof integrations] ? 'Connected' : 'Disconnected'}
                      </span>
                      <div className="relative inline-block w-12 h-6 align-middle select-none transition duration-200 ease-in">
                        <input 
                          type="checkbox"
                          id={`${item.id}-toggle`}
                          checked={integrations[item.id as keyof typeof integrations]}
                          onChange={() => toggleIntegration(item.id as keyof typeof integrations)}
                          className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer border-gray-300 dark:border-gray-600 transition-all duration-300 z-10 checked:right-0 checked:border-primary"
                        />
                        <label 
                          htmlFor={`${item.id}-toggle`}
                          className={`toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-700 cursor-pointer transition-colors duration-300 ${
                            integrations[item.id as keyof typeof integrations] ? 'bg-primary' : ''
                          }`}
                        ></label>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Bottom Form Actions */}
            <div className="flex justify-end gap-4 pt-4 pb-12">
              <button 
                onClick={() => handleAction('Cancel Changes')}
                className="px-6 py-2.5 rounded-lg text-sm font-bold text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors"
                type="button"
              >
                Cancel
              </button>
              <button 
                onClick={handleSave}
                className="px-6 py-2.5 rounded-lg text-sm font-bold bg-primary text-text-main hover:bg-[#71cdc4] transition-colors shadow-md shadow-primary/20"
                type="button"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Settings Specific CSS for Toggle */}
      <style>{`
        .toggle-checkbox:checked {
          right: 0;
        }
      `}</style>
    </div>
  );
};

export default Settings;
