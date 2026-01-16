
import React from 'react';
import { GenerationType } from '../services/geminiService';

interface QuickActionsProps {
  onAction: (prompt: string, type: GenerationType) => void;
}

const QuickActions: React.FC<QuickActionsProps> = ({ onAction }) => {
  const actions = [
    { label: "Generate Product Copy", icon: "description", color: "text-orange-500", type: GenerationType.TEXT, prompt: "Create a persuasive product description for high-end noise cancelling headphones." },
    { label: "Create Listing Images", icon: "image", color: "text-blue-500", type: GenerationType.IMAGE, prompt: "Professional product photography of a sleek glass water bottle on a marble table." },
    { label: "Produce Ad Video", icon: "videocam", color: "text-pink-500", type: GenerationType.VIDEO, prompt: "A cinematic reveal of a new smartwatch on a minimalist pedestal." },
    { label: "Analyze Competitors", icon: "analytics", color: "text-teal-500", type: GenerationType.SEARCH, prompt: "What are the latest pricing trends for luxury skincare products in 2024?" }
  ];

  return (
    <div className="flex flex-wrap justify-center gap-3 pt-4">
      {actions.map((action, idx) => (
        <button 
          key={idx}
          onClick={() => onAction(action.prompt, action.type)}
          className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full shadow-sm hover:shadow-md hover:border-primary/50 dark:hover:border-primary/50 transition-all group"
        >
          <span className={`material-icons-round ${action.color} text-sm group-hover:scale-110 transition-transform`}>{action.icon}</span>
          <span className="text-sm font-medium text-slate-600 dark:text-slate-300">{action.label}</span>
        </button>
      ))}
    </div>
  );
};

export default QuickActions;
