
import React from 'react';
import { AppView } from '../App';

interface SidebarProps {
  currentView: AppView;
  onNavigate: (view: AppView) => void;
  onProjectClick?: (project: any) => void;
  onUpgradeClick?: () => void;
  onProfileClick?: () => void;
  selectedProjectName?: string;
}

const Sidebar: React.FC<SidebarProps> = ({ currentView, onNavigate, onProjectClick, onUpgradeClick, onProfileClick, selectedProjectName }) => {
  const recentProjects = [
    { name: "Summer Campaign", color: "bg-primary" },
    { name: "Nike Air Promo", color: "bg-blue-400" },
    { name: "Organic Coffee Beans", color: "bg-orange-400" }
  ];

  return (
    <aside className="hidden md:flex w-64 bg-white dark:bg-[#1a2626] border-r border-[#e6eaea] dark:border-[#2a3b3b] flex-shrink-0 flex flex-col justify-between h-full transition-colors duration-300 z-20">
      <div className="flex flex-col h-full overflow-hidden">
        <div 
          onClick={() => onNavigate('home')}
          className="flex h-16 items-center px-6 border-b border-[#e6eaea] dark:border-[#2a3b3b] cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
        >
          <span className="material-symbols-outlined text-primary mr-2" style={{ fontSize: '24px' }}>auto_awesome</span>
          <h1 className="text-[#0f1a19] dark:text-white text-lg font-bold">CommerceAI</h1>
        </div>

        <nav className="flex-1 overflow-y-auto sidebar-scroll p-4 space-y-6">
          <div className="flex flex-col gap-1">
            <div className="px-3 py-2 text-xs font-semibold text-[#568f8c] dark:text-[#8ab3b0] uppercase tracking-wider">Menu</div>
            <button 
              onClick={() => onNavigate('home')}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${currentView === 'home' ? 'bg-[#e9f2f1] dark:bg-[#2a3b3b]' : 'hover:bg-[#e9f2f1] dark:hover:bg-[#2a3b3b]'}`}
            >
              <span className={`material-symbols-outlined ${currentView === 'home' ? 'text-[#0f1a19] dark:text-white' : 'text-[#568f8c] dark:text-[#8ab3b0] group-hover:text-[#0f1a19] dark:group-hover:text-white'}`} style={{ fontSize: '20px' }}>home</span>
              <span className="text-[#0f1a19] dark:text-white text-sm font-medium">Home</span>
            </button>
            <button 
              onClick={() => onNavigate('gallery')}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${currentView === 'gallery' ? 'bg-[#e9f2f1] dark:bg-[#2a3b3b]' : 'hover:bg-[#e9f2f1] dark:hover:bg-[#2a3b3b]'}`}
            >
              <span className={`material-symbols-outlined ${currentView === 'gallery' ? 'text-[#0f1a19] dark:text-white' : 'text-[#568f8c] dark:text-[#8ab3b0] group-hover:text-[#0f1a19] dark:group-hover:text-white'}`} style={{ fontSize: '20px' }}>photo_library</span>
              <span className="text-[#0f1a19] dark:text-white text-sm font-medium">Gallery</span>
            </button>
          </div>

          <div className="flex flex-col gap-1">
            <div className="px-3 py-2 text-xs font-semibold text-[#568f8c] dark:text-[#8ab3b0] uppercase tracking-wider">Recent Projects</div>
            <button 
              onClick={() => onNavigate('projects')}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg font-medium transition-all shadow-sm ${
                currentView === 'projects' 
                ? 'bg-[#e9f2f1] dark:bg-[#2a3b3b] text-[#0f1a19] dark:text-white border-l-4 border-primary' 
                : 'text-slate-600 dark:text-slate-400 hover:bg-[#e9f2f1] dark:hover:bg-[#2a3b3b]'
              }`}
            >
              <span className={`material-symbols-outlined ${currentView === 'projects' ? 'text-primary' : 'text-[#568f8c]'}`} style={{ fontSize: '20px' }}>folder_open</span>
              <span className="text-sm">All Projects</span>
            </button>
            {recentProjects.map((proj, idx) => (
              <button 
                key={idx}
                onClick={() => onProjectClick?.({ title: proj.name, type: 'project' })}
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-[#e9f2f1] dark:hover:bg-[#2a3b3b] transition-colors group"
              >
                <span className={`w-1.5 h-1.5 rounded-full ${proj.color} group-hover:shadow-[0_0_8px_rgba(129,216,208,0.6)] transition-shadow`}></span>
                <span className="truncate text-sm">{proj.name}</span>
              </button>
            ))}
          </div>

          <div className="flex flex-col gap-1">
            <div className="px-3 py-2 text-xs font-semibold text-[#568f8c] dark:text-[#8ab3b0] uppercase tracking-wider">System</div>
            <button onClick={() => onNavigate('insights')} className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${currentView === 'insights' ? 'bg-[#e9f2f1] dark:bg-[#2a3b3b]' : 'hover:bg-[#e9f2f1] dark:hover:bg-[#2a3b3b]'}`}>
              <span className="material-symbols-outlined text-[#568f8c] group-hover:text-[#0f1a19] dark:text-[#8ab3b0]" style={{ fontSize: '20px' }}>insights</span>
              <span className="text-[#0f1a19] dark:text-white text-sm font-medium">Insights</span>
            </button>
            <button onClick={() => onNavigate('settings')} className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${currentView === 'settings' ? 'bg-[#e9f2f1] dark:bg-[#2a3b3b]' : 'hover:bg-[#e9f2f1] dark:hover:bg-[#2a3b3b]'}`}>
              <span className="material-symbols-outlined text-[#568f8c] group-hover:text-[#0f1a19] dark:text-[#8ab3b0]" style={{ fontSize: '20px' }}>settings</span>
              <span className="text-[#0f1a19] dark:text-white text-sm font-medium">Settings</span>
            </button>
            <button onClick={() => onNavigate('help-support')} className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${currentView === 'help-support' ? 'bg-[#e9f2f1] dark:bg-[#2a3b3b]' : 'hover:bg-[#e9f2f1] dark:hover:bg-[#2a3b3b]'}`}>
              <span className="material-symbols-outlined text-[#568f8c] group-hover:text-[#0f1a19] dark:text-[#8ab3b0]" style={{ fontSize: '20px' }}>help</span>
              <span className="text-[#0f1a19] dark:text-white text-sm font-medium">Help & Support</span>
            </button>
          </div>
        </nav>
      </div>

      <div className="border-t border-[#e6eaea] dark:border-[#2a3b3b] p-4 bg-white dark:bg-[#1a2626]">
        <div className="mb-4 rounded-xl bg-gradient-to-br from-[#81D8D0]/20 to-[#81D8D0]/5 p-4">
          <div className="flex items-center gap-3 mb-2">
            <span className="material-symbols-outlined text-primary" style={{ fontSize: '24px' }}>diamond</span>
            <h3 className="text-sm font-bold text-[#0f1a19] dark:text-white">Upgrade to Pro</h3>
          </div>
          <p className="text-xs text-[#568f8c] dark:text-[#8ab3b0] mb-3 leading-relaxed">Unlock advanced AI tools and unlimited generation.</p>
          <button onClick={onUpgradeClick} className="w-full rounded-lg bg-[#0f1a19] dark:bg-white text-white dark:text-[#0f1a19] py-2 text-xs font-bold hover:opacity-90 transition-opacity">
            Upgrade Now
          </button>
        </div>
        <div 
          onClick={onProfileClick}
          className="flex items-center gap-3 px-2 pt-2 hover:bg-[#f6f8f8] dark:hover:bg-[#2a3b3b] rounded-lg transition-colors cursor-pointer py-2 group"
        >
          <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-9 border border-[#e6eaea] dark:border-[#2a3b3b]" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuAE3z6Fwx1BMbzVeEg57dW00cRANQ7c09M-W0l8XiL0eD24zr7W1anLy3fK1Uqt0_o_37ZIl_kntuGnVPUJYDZsDz9BFLBnb5NYeJIqnvK1COR3I8LpReBa-eOgYCYzKyJNJdpwCQjHxdXFB6jvSVIKoBHY2uGojnn_abTkQsl1E9emDBs_zlZmejk-1x_IIG38Oolxu7vOfvSsFBN5lasA0OqlPulmY01Y-w_JQKofREHUlGUyJsLZFQtsF3VPi5kDN5ejdqm7ZwA")' }}></div>
          <div className="flex flex-col justify-center overflow-hidden">
            <h1 className="text-[#0f1a19] dark:text-white text-sm font-semibold leading-none truncate group-hover:text-primary transition-colors">Sarah Connor</h1>
            <p className="text-[#568f8c] dark:text-[#8ab3b0] text-xs font-normal pt-1 truncate">sarah@example.com</p>
          </div>
          <span className="material-symbols-outlined text-[#568f8c] ml-auto" style={{ fontSize: '20px' }}>more_vert</span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
