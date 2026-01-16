
import React from 'react';
import { AppView } from '../App';

interface SidebarProps {
  currentView: AppView;
  onNavigate: (view: AppView) => void;
  onProjectClick?: (project: any) => void;
  onUpgradeClick?: () => void;
  selectedProjectName?: string;
}

const Sidebar: React.FC<SidebarProps> = ({ currentView, onNavigate, onProjectClick, onUpgradeClick, selectedProjectName }) => {
  const recentProjects = [
    { name: "Summer Campaign", color: "bg-primary" },
    { name: "Nike Air Promo", color: "bg-blue-400" },
    { name: "Organic Coffee Beans", color: "bg-orange-400" }
  ];

  return (
    <aside className="hidden md:flex w-64 bg-surface-light dark:bg-surface-dark border-r border-border-light dark:border-border-dark flex-shrink-0 flex flex-col justify-between h-full transition-colors duration-300 z-20">
      <div className="flex flex-col h-full overflow-hidden">
        <div className="p-6 flex items-center gap-3 border-b border-border-light dark:border-border-dark">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white shadow-lg shadow-teal-500/30">
            <span className="material-icons-round text-lg">auto_awesome</span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">Commerce<span className="text-primary">AI</span></h1>
        </div>

        <nav className="flex-1 overflow-y-auto sidebar-scroll px-3 py-6 space-y-6">
          <div>
            <div className="px-3 mb-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Menu</span>
            </div>
            <ul className="space-y-1">
              <li>
                <button 
                  onClick={() => onNavigate('home')}
                  className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-lg transition-colors group ${
                    currentView === 'home' 
                    ? 'bg-primary/10 text-teal-700 font-medium dark:bg-primary/20 dark:text-teal-200' 
                    : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <span className={`material-icons-round text-[20px] transition-colors ${currentView === 'home' ? 'text-primary' : 'group-hover:text-primary'}`}>home</span>
                  <span className="text-sm">Home</span>
                </button>
              </li>
              <li>
                <button 
                  onClick={() => onNavigate('gallery')}
                  className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-lg transition-colors group ${
                    currentView === 'gallery' 
                    ? 'bg-primary/10 text-teal-700 font-medium dark:bg-primary/20 dark:text-teal-200' 
                    : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <span className={`material-icons-round text-[20px] transition-colors ${currentView === 'gallery' ? 'text-primary' : 'group-hover:text-primary'}`}>grid_view</span>
                  <span className="text-sm">Gallery</span>
                </button>
              </li>
              <li>
                <button 
                  onClick={() => onNavigate('templates')}
                  className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-lg transition-colors group ${
                    currentView === 'templates' 
                    ? 'bg-primary/10 text-teal-700 font-medium dark:bg-primary/20 dark:text-teal-200' 
                    : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <span className={`material-icons-round text-[20px] transition-colors ${currentView === 'templates' ? 'text-primary' : 'group-hover:text-primary'}`}>dashboard</span>
                  <span className="text-sm">Templates</span>
                </button>
              </li>
            </ul>
          </div>

          <div>
            <div className="px-3 mb-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Recent Projects</span>
            </div>
            <ul className="space-y-1">
              <li>
                <button 
                  onClick={() => onNavigate('projects')}
                  className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg transition-colors group ${
                    currentView === 'projects' 
                    ? 'bg-[#e9f2f1] dark:bg-[#2a3b3b] text-[#0f1a19] dark:text-white font-medium border-l-4 border-primary' 
                    : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <span className={`material-icons-round text-[20px] ${currentView === 'projects' ? 'text-primary' : 'group-hover:text-primary'}`}>folder_open</span>
                  <span className="text-sm">All Projects</span>
                </button>
              </li>
              {recentProjects.map((proj, idx) => (
                <li key={idx}>
                  <button 
                    onClick={() => onProjectClick?.({ title: proj.name, type: 'project' })}
                    className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg transition-colors group ${
                      selectedProjectName === proj.name && currentView === 'asset-detail'
                      ? 'bg-primary/10 text-teal-700 font-bold dark:bg-primary/20 dark:text-teal-200' 
                      : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200'
                    }`}
                  >
                    <span className={`w-1.5 h-1.5 rounded-full ${proj.color} group-hover:shadow-[0_0_8px_rgba(129,216,208,0.6)] transition-shadow`}></span>
                    <span className="truncate text-sm">{proj.name}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <div className="px-3 mb-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Workspace</span>
            </div>
            <ul className="space-y-1">
              <li>
                <button 
                  onClick={() => onNavigate('editor')}
                  className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-lg transition-colors group ${
                    currentView === 'editor' 
                    ? 'bg-primary/10 text-teal-700 font-medium dark:bg-primary/20 dark:text-teal-200' 
                    : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <div className={`absolute left-0 h-6 w-1 bg-primary rounded-r-md ${currentView === 'editor' ? 'block' : 'hidden'}`}></div>
                  <span className={`material-icons-round text-[20px] transition-colors ${currentView === 'editor' ? 'text-primary' : 'group-hover:text-primary'}`}>folder_shared</span>
                  <span className="text-sm">Project</span>
                </button>
              </li>
              <li>
                <button 
                  onClick={() => onNavigate('assets')}
                  className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-lg transition-colors group ${
                    currentView === 'assets' 
                    ? 'bg-primary/10 text-teal-700 font-medium dark:bg-primary/20 dark:text-teal-200' 
                    : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <span className={`material-icons-round text-[20px] transition-colors ${currentView === 'assets' ? 'text-primary' : 'group-hover:text-primary'}`}>photo_library</span>
                  <span className="text-sm">Assets</span>
                </button>
              </li>
              <li>
                <button 
                  onClick={() => onNavigate('insights')}
                  className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-lg transition-colors group ${
                    currentView === 'insights' 
                    ? 'bg-primary/10 text-teal-700 font-medium dark:bg-primary/20 dark:text-teal-200 border-l-2 border-primary' 
                    : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <span className={`material-icons-round text-[20px] transition-colors ${currentView === 'insights' ? 'text-primary' : 'group-hover:text-primary'}`}>analytics</span>
                  <span className="text-sm">Insights</span>
                </button>
              </li>
            </ul>
          </div>

          <div>
            <div className="px-3 mb-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">System</span>
            </div>
            <ul className="space-y-1">
              <li>
                <button 
                  onClick={() => onNavigate('settings')}
                  className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-lg transition-colors group ${
                    currentView === 'settings' 
                    ? 'bg-primary/10 text-teal-700 font-medium dark:bg-primary/20 dark:text-teal-200' 
                    : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <span className={`material-icons-round text-[20px] transition-colors ${currentView === 'settings' ? 'text-primary' : 'group-hover:text-primary'}`}>settings</span>
                  <span className="text-sm">Settings</span>
                </button>
              </li>
              <li>
                <button 
                  onClick={() => onNavigate('help-support')}
                  className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-lg transition-colors group ${
                    currentView === 'help-support' 
                    ? 'bg-primary/10 text-teal-700 font-medium dark:bg-primary/20 dark:text-teal-200 border-l-2 border-primary' 
                    : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <span className={`material-icons-round text-[20px] transition-colors ${currentView === 'help-support' ? 'text-primary' : 'group-hover:text-primary'}`}>help</span>
                  <span className="text-sm">Help & Support</span>
                </button>
              </li>
            </ul>
          </div>
        </nav>
      </div>

      <div className="p-4 border-t border-border-light dark:border-border-dark space-y-4 bg-surface-light dark:bg-surface-dark z-10">
        <div className="bg-gradient-to-br from-teal-50 to-cyan-50 dark:from-teal-900/20 dark:to-cyan-900/20 p-4 rounded-xl border border-teal-100 dark:border-teal-800/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-teal-700 dark:text-teal-300 uppercase tracking-wider">Pro Plan</span>
            <span className="bg-primary text-white text-[10px] px-1.5 py-0.5 rounded-full">NEW</span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">Unlock advanced AI tools and unlimited generation.</p>
          <button 
            onClick={onUpgradeClick}
            className="w-full bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark text-xs font-bold py-1.5 rounded-lg shadow-sm hover:shadow transition-shadow text-slate-900 dark:text-white hover:text-primary hover:border-primary"
          >
            Upgrade Now
          </button>
        </div>
        <button className="flex items-center gap-3 w-full p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors text-left group">
          <div className="relative">
            <img alt="User Avatar" className="w-9 h-9 rounded-full border-2 border-white dark:border-gray-700 shadow-sm" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAE3z6Fwx1BMbzVeEg57dW00cRANQ7c09M-W0l8XiL0eD24zr7W1anLy3fK1Uqt0_o_37ZIl_kntuGnVPUJYDZsDz9BFLBnb5NYeJIqnvK1COR3I8LpReBa-eOgYCYzKyJNJdpwCQjHxdXFB6jvSVIKoBHY2uGojnn_abTkQsl1E9emDBs_zlZmejk-1x_IIG38Oolxu7vOfvSsFBN5lasA0OqlPulmY01Y-w_JQKofREHUlGUyJsLZFQtsF3VPi5kDN5ejdqm7ZwA" />
            <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-500 border-2 border-white dark:border-surface-dark rounded-full"></span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-900 dark:text-white truncate group-hover:text-primary transition-colors">Sarah Connor</p>
            <p className="text-xs text-slate-500 dark:text-slate-400 truncate">sarah@example.com</p>
          </div>
          <span className="material-icons-round text-slate-400 group-hover:text-primary transition-colors">expand_more</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
