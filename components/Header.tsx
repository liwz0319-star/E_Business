
import React from 'react';

interface HeaderProps {
  darkMode: boolean;
  onToggleDarkMode: () => void;
  onNotificationClick?: () => void;
}

const Header: React.FC<HeaderProps> = ({ darkMode, onToggleDarkMode, onNotificationClick }) => {
  return (
    <header className="flex items-center justify-between px-8 py-4 z-10">
      <div className="flex items-center gap-2 text-slate-400 text-sm">
        <span className="hover:text-slate-600 dark:hover:text-slate-300 cursor-pointer">Dashboard</span>
        <span className="material-icons-round text-[14px]">chevron_right</span>
        <span className="text-slate-800 dark:text-slate-200 font-medium">New Project</span>
      </div>
      <div className="flex items-center gap-4">
        <button 
          onClick={onToggleDarkMode}
          className="p-2 rounded-full text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-primary transition-colors"
        >
          <span className="material-icons-round">{darkMode ? 'light_mode' : 'dark_mode'}</span>
        </button>
        <button 
          onClick={onNotificationClick}
          className="p-2 rounded-full text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-primary transition-colors relative"
        >
          <span className="material-icons-round">notifications</span>
          <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
      </div>
    </header>
  );
};

export default Header;
