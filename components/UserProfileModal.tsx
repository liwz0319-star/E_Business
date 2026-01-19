
import React, { useState, useRef } from 'react';

interface UserProfileModalProps {
  onClose: () => void;
}

const UserProfileModal: React.FC<UserProfileModalProps> = ({ onClose }) => {
  const [avatarUrl, setAvatarUrl] = useState('https://lh3.googleusercontent.com/aida-public/AB6AXuDFJY6bNlH850Ma0pbfUM7nJLfDjyz9RBRymIG9KLrnufxgvutJPFr5cvCd0z2S4i0SwY6lxusVj7gtr2ngg3wCijLeRHbwmyyGgfMz6Oji6SlbrKPZCul8Q_FLWsjaXkXWLFiINJ9KVeVpoxIYIAJJSDyfayY87CaPRcwzWKgRJh1XKM68hgt1ldkPG1HO0SVUUKBC7Ja1XNTlHQ4Umf91U8aJJVpNRTva09N6PKd2EBlluuICzZQB0WNq6cJPu5mNoA85xysPtz9G');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleAvatarEditClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSave = () => {
    alert("Profile changes saved successfully!");
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-3 sm:p-4 md:p-6 font-display overflow-hidden">
      {/* Backdrop */}
      <div
        aria-hidden="true"
        className="fixed inset-0 bg-black/30 backdrop-blur-md z-40 transition-opacity"
        onClick={onClose}
      ></div>

      {/* Modal Container: Responsive width and max-height */}
      <div className="relative z-50 flex w-full max-w-[95%] sm:max-w-lg flex-col overflow-hidden rounded-2xl bg-white border border-primary/40 shadow-2xl dark:bg-background-dark animate-fade-in-up transition-all duration-300 max-h-[92vh]">

        {/* Responsive Close Button */}
        <button
          onClick={onClose}
          className="absolute top-3 right-3 sm:top-4 sm:right-4 z-20 flex h-8 w-8 items-center justify-center rounded-full bg-slate-50 text-text-main hover:bg-slate-100 dark:bg-white/10 dark:text-white dark:hover:bg-white/20 transition-colors shadow-sm"
        >
          <span className="material-symbols-outlined text-xl">close</span>
        </button>

        {/* Scrollable Content Area */}
        <main className="flex-1 overflow-y-auto sidebar-scroll p-3 sm:p-4">
          <div className="flex flex-col items-center space-y-2 sm:space-y-3">

            {/* Header Section */}
            <div className="text-center w-full px-2">
              <h2 className="text-lg sm:text-xl font-bold tracking-tight text-text-main dark:text-white uppercase tracking-[0.05em]">Merchant Profile</h2>
              <p className="text-[10px] sm:text-xs text-text-secondary dark:text-gray-400 mt-0.5">Manage your professional store identity</p>
            </div>

            {/* Avatar Section: Responsive sizing */}
            <div className="relative group">
              <div className="size-16 sm:size-20 rounded-full border-4 border-white shadow-xl overflow-hidden dark:border-[#2a3837]">
                <div
                  className="h-full w-full bg-slate-100 bg-cover bg-center transition-all duration-500"
                  style={{ backgroundImage: `url('${avatarUrl}')` }}
                ></div>
              </div>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/*"
                className="hidden"
              />
              <button
                onClick={handleAvatarEditClick}
                className="absolute bottom-0 right-0 sm:bottom-1 sm:right-1 flex h-8 w-8 sm:h-9 sm:w-9 cursor-pointer items-center justify-center rounded-full border-2 border-white bg-primary text-slate-900 shadow-md transition hover:bg-secondary dark:border-[#2a3837] transform hover:scale-110 active:scale-95"
              >
                <span className="material-symbols-outlined text-[16px] sm:text-[18px] font-bold">edit</span>
              </button>
            </div>

            {/* Form Section */}
            <form className="w-full space-y-2 sm:space-y-3" onSubmit={(e) => e.preventDefault()}>
              <div className="space-y-1.5">
                <label className="text-[11px] sm:text-xs font-bold text-text-main dark:text-gray-200 ml-1 uppercase tracking-wider">User Name</label>
                <div className="relative group">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary group-focus-within:text-primary transition-colors text-xl">person</span>
                  <input
                    className="w-full rounded-xl border border-border-color bg-slate-50 py-1.5 sm:py-2 pl-10 pr-4 text-sm sm:text-base text-text-main placeholder-text-secondary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary dark:border-[#2a3837] dark:bg-[#1a2625] dark:text-white transition-all font-medium"
                    type="text"
                    defaultValue="Sarah Connor"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[11px] sm:text-xs font-bold text-text-main dark:text-gray-200 ml-1 uppercase tracking-wider">Linked Email</label>
                <div className="relative flex items-center group">
                  <span className="material-symbols-outlined absolute left-3 z-10 text-text-secondary group-focus-within:text-primary transition-colors text-xl">mail</span>
                  <input
                    className="w-full rounded-xl border border-border-color bg-slate-50 py-1.5 sm:py-2 pl-10 pr-12 text-sm sm:text-base text-text-main placeholder-text-secondary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary dark:border-[#2a3837] dark:bg-[#1a2625] dark:text-white transition-all font-medium"
                    type="email"
                    defaultValue="sarah@example.com"
                  />
                  <span className="material-symbols-outlined absolute right-3 text-green-500 font-bold" title="Verified">check_circle</span>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[11px] sm:text-xs font-bold text-text-main dark:text-gray-200 ml-1 uppercase tracking-wider">Personal Bio</label>
                <div className="relative group">
                  <span className="material-symbols-outlined absolute left-3 top-2 text-text-secondary group-focus-within:text-primary transition-colors text-xl">description</span>
                  <textarea
                    className="w-full rounded-xl border border-border-color bg-slate-50 py-1.5 sm:py-2 pl-10 pr-4 text-sm sm:text-base text-text-main placeholder-text-secondary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary dark:border-[#2a3837] dark:bg-[#1a2625] dark:text-white transition-all font-medium min-h-[40px] sm:min-h-[60px] resize-none"
                    placeholder="Tell us about yourself..."
                    defaultValue="E-commerce specialist focused on high-converting product visuals and professional copy generation."
                  />
                </div>
              </div>
            </form>

            {/* Stats Grid: Always 2 columns but adjusts padding */}
            <div className="w-full grid grid-cols-2 gap-2 sm:gap-3">
              <button
                onClick={() => alert("Redirecting to Creations Gallery...")}
                className="flex flex-col items-center justify-center rounded-2xl border border-border-color bg-white p-2 sm:p-3 text-center shadow-sm transition-all hover:border-primary/50 dark:border-[#2a3837] dark:bg-[#1a2625] hover:shadow-md active:scale-[0.98]"
              >
                <div className="mb-1 flex size-6 sm:size-8 items-center justify-center rounded-full bg-primary/10 text-primary dark:bg-primary/20">
                  <span className="material-symbols-outlined text-[16px] sm:text-[18px]">photo_library</span>
                </div>
                <h4 className="text-lg sm:text-xl font-black text-text-main dark:text-white leading-none">2,845</h4>
                <p className="text-[8px] sm:text-[9px] font-black text-text-secondary dark:text-gray-400 uppercase tracking-[0.1em] mt-0.5">Creations</p>
              </button>
              <button
                onClick={() => alert("Viewing usage statistics...")}
                className="flex flex-col items-center justify-center rounded-2xl border border-border-color bg-white p-2 sm:p-3 text-center shadow-sm transition-all hover:border-primary/50 dark:border-[#2a3837] dark:bg-[#1a2625] hover:shadow-md active:scale-[0.98]"
              >
                <div className="mb-1 flex size-6 sm:size-8 items-center justify-center rounded-full bg-primary/10 text-primary dark:bg-primary/20">
                  <span className="material-symbols-outlined text-[16px] sm:text-[18px]">calendar_month</span>
                </div>
                <h4 className="text-lg sm:text-xl font-black text-text-main dark:text-white leading-none">124</h4>
                <p className="text-[8px] sm:text-[9px] font-black text-text-secondary dark:text-gray-400 uppercase tracking-[0.1em] mt-0.5">Active Days</p>
              </button>
            </div>

            {/* Pro Status Banner: Responsive layout */}
            <div className="w-full relative overflow-hidden rounded-2xl bg-gradient-to-r from-primary/20 to-primary/5 p-2 sm:p-3 shadow-sm dark:from-primary/10 dark:to-transparent border border-primary/20">
              <div className="absolute -right-6 -top-10 h-32 w-32 rounded-full bg-primary/30 blur-2xl pointer-events-none"></div>
              <div className="relative z-10 flex flex-col gap-4">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 sm:gap-3">
                    <div className="flex size-10 sm:size-11 items-center justify-center rounded-xl bg-white/80 text-text-main shadow-sm backdrop-blur-sm dark:bg-white/10 dark:text-primary border border-white/50 shrink-0">
                      <span className="material-symbols-outlined text-xl sm:text-2xl font-bold">workspace_premium</span>
                    </div>
                    <div className="flex flex-col text-left overflow-hidden">
                      <h3 className="text-sm sm:text-base font-black text-text-main dark:text-white tracking-tight truncate">Pro Member</h3>
                      <span className="text-[9px] sm:text-[11px] font-bold text-text-main/60 dark:text-gray-400 truncate">Renews Oct 24, 2024</span>
                    </div>
                  </div>
                  <button
                    onClick={() => alert("Opening subscription management...")}
                    className="rounded-full bg-primary text-slate-900 px-2 sm:px-3 py-1 text-[9px] sm:text-[10px] font-black uppercase tracking-wider shadow-sm hover:bg-secondary transition-colors whitespace-nowrap"
                  >
                    Active
                  </button>
                </div>
              </div>
            </div>

            {/* Action Button */}
            <div className="w-full pt-2">
              <button
                onClick={handleSave}
                className="w-full rounded-xl bg-primary py-2.5 sm:py-3 text-sm font-black text-slate-900 shadow-xl shadow-primary/20 transition-all hover:bg-secondary hover:-translate-y-0.5 active:translate-y-0 active:scale-95"
              >
                Save Changes
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default UserProfileModal;
