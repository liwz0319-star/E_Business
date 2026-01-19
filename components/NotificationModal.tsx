
import React from 'react';

interface NotificationModalProps {
  onClose: () => void;
}

const NotificationModal: React.FC<NotificationModalProps> = ({ onClose }) => {
  const notifications = [
    {
      id: 1,
      title: "AI Generation Complete",
      description: "Your \"Summer Collection\" product images have been generated and are ready for review.",
      time: "2m ago",
      icon: "auto_awesome",
      iconBg: "bg-gradient-to-br from-primary/20 to-primary/5",
      iconColor: "text-primary-dark",
      unread: true
    },
    {
      id: 2,
      title: "Subscription Renewal",
      description: "Your Pro plan is set to renew tomorrow. Please ensure your payment method is up to date.",
      time: "1h ago",
      icon: "notifications_active",
      iconBg: "bg-orange-50 dark:bg-orange-500/10",
      iconColor: "text-orange-500",
      unread: true
    },
    {
      id: 3,
      title: "New Order #2841",
      description: "New order received from Michael B. for $124.50.",
      time: "3h ago",
      icon: "shopping_bag",
      iconBg: "bg-blue-50 dark:bg-blue-500/10",
      iconColor: "text-blue-500",
      unread: false
    },
    {
      id: 4,
      title: "Traffic Spike",
      description: "Your store traffic is up by 45% compared to last week's average.",
      time: "5h ago",
      icon: "trending_up",
      iconBg: "bg-green-50 dark:bg-green-500/10",
      iconColor: "text-green-500",
      unread: false
    },
    {
      id: 5,
      title: "System Maintenance",
      description: "Scheduled maintenance completed successfully. All systems operational.",
      time: "1d ago",
      icon: "dns",
      iconBg: "bg-gray-100 dark:bg-white/10",
      iconColor: "text-gray-500 dark:text-gray-400",
      unread: false
    }
  ];

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 md:p-8 font-display">
      {/* Backdrop */}
      <div 
        aria-hidden="true" 
        className="fixed inset-0 bg-black/20 backdrop-blur-md z-40 transition-opacity"
        onClick={onClose}
      ></div>

      {/* Modal Container */}
      <div className="relative z-50 flex w-full max-w-[95%] sm:max-w-lg flex-col overflow-hidden rounded-2xl bg-white border border-primary/40 shadow-2xl dark:bg-background-dark animate-fade-in-up transition-all duration-300 max-h-[85vh]">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-100 dark:border-white/5 bg-white/80 dark:bg-background-dark/80 backdrop-blur-sm z-10 shrink-0">
          <h2 className="text-xl font-bold tracking-tight text-text-main dark:text-white">Notifications</h2>
          <button 
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-50 text-text-main hover:bg-slate-100 dark:bg-white/10 dark:text-white dark:hover:bg-white/20 transition-colors"
          >
            <span className="material-symbols-outlined text-xl">close</span>
          </button>
        </div>

        {/* List Content */}
        <main className="sidebar-scroll flex-1 overflow-y-auto">
          <div className="divide-y divide-slate-100 dark:divide-white/5">
            {notifications.map((notif) => (
              <div 
                key={notif.id}
                className={`group relative flex gap-4 p-5 transition-colors hover:bg-slate-50 dark:hover:bg-white/5 cursor-pointer ${notif.unread ? 'bg-primary/5 dark:bg-primary/10' : ''}`}
              >
                {notif.unread && (
                  <div className="absolute right-5 top-6 h-2.5 w-2.5 rounded-full bg-primary shadow-[0_0_8px_rgba(129,216,208,0.6)]"></div>
                )}
                <div className="flex-shrink-0">
                  <div className={`flex h-10 w-10 items-center justify-center rounded-full ${notif.iconBg} ${notif.iconColor}`}>
                    <span className="material-symbols-outlined text-[20px]">{notif.icon}</span>
                  </div>
                </div>
                <div className="flex-1 pr-6 overflow-hidden">
                  <div className="mb-1 flex items-center justify-between gap-2">
                    <h3 className="text-sm font-bold text-text-main dark:text-white truncate">{notif.title}</h3>
                    <span className="text-[11px] font-medium text-text-secondary dark:text-gray-400 whitespace-nowrap">{notif.time}</span>
                  </div>
                  <p className="text-xs leading-relaxed text-text-secondary dark:text-gray-400 line-clamp-2">
                    {notif.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </main>

        {/* Footer */}
        <div className="p-6 pt-4 border-t border-slate-100 dark:border-white/5 bg-white dark:bg-background-dark shrink-0">
          <button 
            onClick={() => alert("All marked as read")}
            className="w-full rounded-xl bg-primary py-3.5 text-sm font-bold text-slate-900 shadow-xl shadow-primary/20 transition-all hover:bg-teal-400 hover:translate-y-[-1px] active:translate-y-[0px] active:scale-95 flex items-center justify-center gap-2"
          >
            <span className="material-symbols-outlined text-[18px]">done_all</span>
            Mark All as Read
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotificationModal;
