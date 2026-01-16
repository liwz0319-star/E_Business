
import React, { useState, useMemo } from 'react';

interface ProjectsProps {
  onNewProject: () => void;
  onAssetClick?: (asset: any) => void;
}

const Projects: React.FC<ProjectsProps> = ({ onNewProject, onAssetClick }) => {
  const [searchQuery, setSearchQuery] = useState('');

  const todayProjects = [
    { id: 1, title: 'Summer Campaign Video v2', type: 'Video', status: 'Generating', progress: 45, time: '10:42 AM', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDOsNo_8An-UkDwEV1h5cBmy-z2nCejF-VhfD7T9uwX1KPm5uYnWlkuOclGwb2ILhR4OGgVMhxL-sbE9qJd4vUyMInZ1nxiSpQJhiUmM0km01pfmdd4rDQCZoIACezl2yb-GK_wRohh_rneG4-WCgoP2IcZpbr43OqsPatVis3w-8Dn3zcdW1mkq-cB0kumesFO33EAeybjnC53yPoI_6tolI5j3-EGOJt3d-FsL0BSHdWnlD34c_dPXjmeQ4QqCWNyBAIMzdZXeKM' },
    { id: 2, title: 'Organic Soap Product Shots', type: 'Image', status: 'Completed', editedBy: 'Sarah', time: '09:15 AM', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuC4iVG0jO1wf8LsxoFHR77m6d18HWs63bLBifMuLxQ-tnsm-XvbfutHYEz5bmfTB3U0W7JLQ8-O2DEUyHUc1OOFsYL6IdgivB0D7nibOjhImtq0FHy3PBbeQohPb8w-Pzp7B-5U3BxMY3rB8IFlX4cPiCXt70HiynQjf9xhou_wR6QQR_LV2mr9kzQAbTyA8kpYO3oH6KVJO7Ujx1nhKrZz520ZgaKopSziRTdzfubaApQZYfUXQFh_w26bf_zk8MDNnkxBkcir8wo' }
  ];

  const yesterdayProjects = [
    { id: 3, title: 'Black Friday Ad Copy', type: 'Copy', status: 'Draft', time: '4:30 PM', isDraft: true },
    { id: 4, title: 'Nike Air Max Gen 2', type: 'Image', status: 'Completed', time: '2:15 PM', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDtAU4Euz9lCVjEtNHvP_8x80eLZpAotsGlAzQPWGK7wSw1cXmkooHfPIBgKCnZScrX0vpr9EmEmvelbwQ6YCu3hdIiR299BDuKAgguBOZ9sTSOj1u41YN4EVPKVBeQ_duDqWuwhuoLEUvR9EOt_fz1aOHZHETQVESPhJ9Sjk32T_J0ALpdtHmUfwB6s0XQvIyn5i0RNcwtFxpoIQyimRQwsCBqst8gk70P1uW9j01mTF_U7z5mHCeYgRhZZLMd425070UL7lC0aj8' }
  ];

  const lastWeekProjects = [
    { id: 5, title: 'Fall Season Texture Pack', type: 'Image', status: 'Completed', time: 'Oct 24', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB0E_2VUUobS20gRf_s5b7pIyrgou3V5NOtBT2NEuDLnTjpXbu396o3QPQjEXEDFy7w0ggkeFf28a9YCbkNTtyNC3hj063_1Mr-e5-9GzwBl-J2V-wQ6kjx2TzslnqAKm5tZywucLWlqe4ioZeRwq0a1UalJAEfG4zCyMercGcAXMu28VwXjqXkZ9T3yt0az-9U2--eLAF1wb5admQkjdm6jiVMyPKwOIUkFGtk5_O-MKO6_zOPO3w7G4MQjyVOXh07qARnRH1dg7A' }
  ];

  const handleAction = (e: React.MouseEvent, action: string, title: string) => {
    e.stopPropagation();
    alert(`${action} project: ${title}`);
  };

  const handleTimelineClick = (e: React.MouseEvent, project: any) => {
    e.stopPropagation();
    onAssetClick?.({ ...project, viewTimeline: true });
  };

  const filteredToday = useMemo(() => todayProjects.filter(p => p.title.toLowerCase().includes(searchQuery.toLowerCase())), [searchQuery]);
  const filteredYesterday = useMemo(() => yesterdayProjects.filter(p => p.title.toLowerCase().includes(searchQuery.toLowerCase())), [searchQuery]);
  const filteredLastWeek = useMemo(() => lastWeekProjects.filter(p => p.title.toLowerCase().includes(searchQuery.toLowerCase())), [searchQuery]);

  return (
    <div className="flex-1 flex flex-col h-full bg-background-light dark:bg-background-dark overflow-y-auto sidebar-scroll transition-colors">
      <div className="mx-auto flex w-full max-w-[1200px] flex-col px-6 py-8 md:px-10 lg:px-12">
        {/* Header Section */}
        <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between mb-8 animate-fade-in-up">
          <div className="flex flex-col gap-2">
            <h1 className="text-[#0f1a19] dark:text-white text-3xl font-black leading-tight tracking-[-0.033em]">Recent Projects</h1>
            <p className="text-[#568f8c] dark:text-[#8ab3b0] text-base font-normal">Manage your AI-generated product content and assets</p>
          </div>
          <div className="flex items-center gap-3">
            <label className="relative flex items-center md:min-w-[320px]">
              <span className="material-symbols-outlined absolute left-3 text-[#568f8c]" style={{ fontSize: '20px' }}>search</span>
              <input 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="h-10 w-full rounded-lg border-none bg-white dark:bg-[#1a2626] dark:text-white pl-10 pr-4 text-sm font-medium placeholder-[#568f8c] focus:outline-none focus:ring-2 focus:ring-primary/50 shadow-sm transition-all" 
                placeholder="Search projects..." 
                type="text"
              />
            </label>
            <button 
              onClick={(e) => handleAction(e, 'Open filters', 'Project Filters')}
              className="flex h-10 w-10 items-center justify-center rounded-lg bg-white dark:bg-[#1a2626] dark:text-white shadow-sm hover:bg-gray-50 dark:hover:bg-[#2a3b3b] transition-all active:scale-95"
            >
              <span className="material-symbols-outlined text-[#568f8c]" style={{ fontSize: '20px' }}>filter_list</span>
            </button>
            <button 
              onClick={onNewProject}
              className="flex h-10 px-4 items-center justify-center gap-2 rounded-lg bg-primary text-[#0f1a19] hover:bg-[#68cdc4] transition-colors shadow-sm dark:text-black font-bold text-sm active:scale-95"
            >
              <span className="material-symbols-outlined text-[20px]">add</span>
              New Project
            </button>
          </div>
        </div>

        {/* Section: Today */}
        {[
          { title: 'Today', items: filteredToday, delay: '0.1s' },
          { title: 'Yesterday', items: filteredYesterday, delay: '0.2s' },
          { title: 'Last Week', items: filteredLastWeek, delay: '0.3s' }
        ].map(section => section.items.length > 0 && (
          <div key={section.title} className="mb-8 animate-fade-in-up" style={{ animationDelay: section.delay }}>
            <h3 className="text-[#0f1a19] dark:text-white text-lg font-bold leading-tight tracking-[-0.015em] mb-4">{section.title}</h3>
            <div className="flex flex-col gap-3">
              {section.items.map(project => (
                <div 
                  key={project.id} 
                  onClick={() => onAssetClick?.(project)}
                  className="group relative flex items-center justify-between gap-4 rounded-xl border border-transparent bg-white dark:bg-[#1a2626] p-4 shadow-sm hover:border-primary/30 transition-all duration-200 cursor-pointer"
                >
                  <div className="flex items-center gap-4 flex-1">
                    <div className="relative h-12 w-12 flex-shrink-0 overflow-hidden rounded-lg bg-gray-100 flex items-center justify-center text-[#568f8c]">
                      {project.img ? (
                        <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url('${project.img}')` }}></div>
                      ) : (
                        <span className="material-symbols-outlined" style={{ fontSize: '24px' }}>description</span>
                      )}
                      {(project as any).status === 'Generating' && (
                        <div className="absolute inset-0 flex items-center justify-center bg-black/20">
                          <span className="material-symbols-outlined animate-spin text-primary" style={{ fontSize: '24px' }}>progress_activity</span>
                        </div>
                      )}
                    </div>
                    <div className="flex flex-col flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h4 className="text-[#0f1a19] dark:text-white text-sm font-semibold truncate">{project.title}</h4>
                        <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${
                          project.type === 'Video' ? 'bg-primary/10 text-primary ring-primary/20' : 
                          project.type === 'Copy' ? 'bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 ring-purple-700/10' :
                          'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 ring-blue-700/10'
                        }`}>
                          {project.type}
                        </span>
                      </div>
                      <div className="mt-1 flex items-center gap-4">
                        {(project as any).status === 'Generating' ? (
                          <>
                            <div className="h-1.5 w-full max-w-[200px] rounded-full bg-gray-100 dark:bg-gray-700 overflow-hidden">
                              <div className="h-full rounded-full bg-primary" style={{ width: `${(project as any).progress}%` }}></div>
                            </div>
                            <span className="text-xs text-primary font-medium">Generating... {(project as any).progress}%</span>
                          </>
                        ) : (
                          <div className="mt-1 flex items-center gap-2 text-xs text-[#568f8c] dark:text-[#8ab3b0]">
                            <span className={`inline-flex items-center gap-1 font-medium ${(project as any).isDraft ? 'text-gray-500' : 'text-green-600 dark:text-green-400'}`}>
                              <span className="material-symbols-outlined text-[14px]">{(project as any).isDraft ? 'draft' : 'check_circle'}</span>
                              {(project as any).isDraft ? 'Draft' : 'Completed'}
                            </span>
                            {(project as any).editedBy && (
                              <>
                                <span>•</span>
                                <span>Edited by {(project as any).editedBy}</span>
                              </>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="hidden sm:flex items-center gap-8 text-sm text-[#568f8c] dark:text-[#8ab3b0]">
                    <span className="whitespace-nowrap">{project.time}</span>
                  </div>
                  <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button 
                      onClick={(e) => handleTimelineClick(e, project)}
                      className="p-2 text-primary hover:bg-primary/10 rounded-lg transition-colors" 
                      title="View Generation Timeline"
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>history</span>
                    </button>
                    <button onClick={(e) => handleAction(e, 'Edit', project.title)} className="p-2 text-[#568f8c] hover:bg-gray-100 dark:hover:bg-[#2a3b3b] rounded-lg transition-colors" title="Edit">
                      <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>edit</span>
                    </button>
                    <button onClick={(e) => handleAction(e, 'Duplicate', project.title)} className="p-2 text-[#568f8c] hover:bg-gray-100 dark:hover:bg-[#2a3b3b] rounded-lg transition-colors" title="Duplicate">
                      <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>content_copy</span>
                    </button>
                    <button onClick={(e) => handleAction(e, 'Delete', project.title)} className="p-2 text-[#568f8c] hover:text-red-500 hover:bg-gray-100 dark:hover:bg-[#2a3b3b] rounded-lg transition-colors" title="Delete">
                      <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>delete</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

        {/* Empty State */}
        {filteredToday.length === 0 && filteredYesterday.length === 0 && filteredLastWeek.length === 0 && (
          <div className="flex flex-col items-center justify-center py-32 text-center">
            <span className="material-symbols-outlined text-6xl text-gray-300 mb-4">folder_off</span>
            <h3 className="text-xl font-bold text-gray-400">No projects found</h3>
            <p className="text-gray-400">Try a different search term or create a new project.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Projects;
