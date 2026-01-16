
import React from 'react';

interface ProjectTimelineProps {
  project?: any;
  onBack: () => void;
}

const ProjectTimeline: React.FC<ProjectTimelineProps> = ({ project, onBack }) => {
  const projectTitle = project?.title || "Product #102 - Summer Sneaker";
  
  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto bg-background-light dark:bg-background-dark font-display text-text-main transition-colors duration-300 antialiased sidebar-scroll">
      <div className="flex flex-1 justify-center p-4 md:p-8 lg:p-12">
        <div className="flex w-full max-w-5xl flex-col gap-8">
          
          {/* Breadcrumbs */}
          <div className="flex flex-wrap gap-2 text-sm">
            <button 
              onClick={onBack}
              className="text-text-secondary hover:text-primary transition-colors font-medium"
            >
              Projects
            </button>
            <span className="text-text-secondary">/</span>
            <span className="text-text-secondary">Winter Campaign</span>
            <span className="text-text-secondary">/</span>
            <span className="font-bold text-text-main dark:text-white">{project?.title || "Product #102"}</span>
          </div>

          {/* Page Header & Actions */}
          <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between animate-fade-in-up">
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-3">
                <h1 className="text-3xl font-black text-text-main dark:text-white tracking-tight">{projectTitle}</h1>
                <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-black text-green-800 dark:bg-green-900/30 dark:text-green-400 uppercase tracking-wider">
                  Completed
                </span>
              </div>
              <p className="text-text-secondary dark:text-gray-400 font-medium">Project ID: 8821 • Created Oct 24, 2023</p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <button className="group flex h-10 items-center justify-center gap-2 rounded-xl bg-surface-light border border-gray-200 px-4 text-sm font-bold text-text-main hover:bg-gray-50 dark:bg-surface-dark dark:border-gray-700 dark:text-white dark:hover:bg-gray-800 transition-all active:scale-95 shadow-sm">
                <span className="material-symbols-outlined text-[20px] text-text-main dark:text-white">download</span>
                <span>Download All</span>
              </button>
              <button className="flex h-10 items-center justify-center gap-2 rounded-xl bg-primary px-6 text-sm font-black text-text-main shadow-lg shadow-primary/20 hover:opacity-90 dark:text-gray-900 transition-all active:scale-95">
                <span className="material-symbols-outlined text-[20px] font-bold">storefront</span>
                <span>Publish to Store</span>
              </button>
            </div>
          </div>

          {/* Main Content Area: Timeline */}
          <div className="flex flex-col gap-8 rounded-3xl bg-white p-6 shadow-xl dark:bg-surface-dark dark:shadow-none lg:p-10 border border-border-light dark:border-border-dark animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            <h2 className="mb-4 text-xl font-black text-text-main dark:text-white flex items-center gap-2">
              <span className="material-symbols-outlined text-primary">timeline</span>
              Generation Timeline
            </h2>
            
            <div className="relative flex flex-col gap-8">
              
              {/* Timeline Line (Static positioning for React) */}
              <div className="absolute left-[19px] top-[40px] bottom-[20px] w-0.5 bg-gray-100 dark:bg-gray-800 z-0"></div>

              {/* Step 1: Image Uploaded */}
              <div className="relative flex gap-6 z-10">
                <div className="flex flex-col items-center">
                  <div className="flex size-10 items-center justify-center rounded-full bg-primary text-text-main shadow-lg ring-4 ring-white dark:ring-surface-dark">
                    <span className="material-symbols-outlined text-[20px] font-black">check</span>
                  </div>
                </div>
                <div className="flex flex-1 flex-col gap-4 pb-4">
                  <div className="flex flex-col">
                    <div className="flex items-baseline justify-between">
                      <h3 className="text-lg font-black text-text-main dark:text-white">Image Uploaded</h3>
                      <span className="text-xs font-bold text-text-secondary uppercase">09:00 AM</span>
                    </div>
                    <p className="text-sm text-text-secondary font-medium">Source file received successfully.</p>
                  </div>
                  <div className="flex items-center gap-4 rounded-2xl border border-gray-100 bg-background-light p-4 dark:border-gray-800 dark:bg-background-dark/50 transition-all hover:border-primary/30">
                    <div className="size-20 shrink-0 rounded-xl bg-cover bg-center shadow-md" style={{ backgroundImage: `url('https://lh3.googleusercontent.com/aida-public/AB6AXuBnLrjckbTmCj3fGQPXcqeoOyBEM_mOrLMXEttoK0fR68H1ooWlZ60fv1dPWSPQtPf4ZVczb5IXdjZ-0MAhyWJEiByINx-P7Y7t6tpQeV-JUmfBEfvK1m-3yBVyPQwxJ16JFk5fze1jxtEKmOoW9bnzlhx6-fdbJa7NkXwiIF5aQoLNWL-8DFa4gJr8MPSzd4NxKgT5AHrO6-iP52ZZ5NzpbspIwOePhPF9QnfmtSY2OCCqhV3RU0paaJK1yWKMPtTlaIb2AJPXW80')` }}></div>
                    <div className="flex flex-col gap-1 overflow-hidden">
                      <p className="truncate text-sm font-black text-text-main dark:text-white">sneaker_front_v1.jpg</p>
                      <p className="text-xs text-text-secondary font-bold">3.2 MB • 4032x3024px</p>
                    </div>
                    <button className="ml-auto rounded-xl p-2.5 text-text-secondary hover:bg-gray-200 hover:text-text-main dark:hover:bg-gray-700 dark:hover:text-white transition-colors">
                      <span className="material-symbols-outlined">visibility</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Step 2: AI Analysis & Background Removal */}
              <div className="relative flex gap-6 z-10">
                <div className="flex flex-col items-center">
                  <div className="flex size-10 items-center justify-center rounded-full bg-primary text-text-main shadow-lg ring-4 ring-white dark:ring-surface-dark">
                    <span className="material-symbols-outlined text-[20px] font-black">check</span>
                  </div>
                </div>
                <div className="flex flex-1 flex-col gap-4 pb-4">
                  <div className="flex flex-col">
                    <div className="flex items-baseline justify-between">
                      <h3 className="text-lg font-black text-text-main dark:text-white">AI Analysis & Background Removal</h3>
                      <span className="text-xs font-bold text-text-secondary uppercase">09:02 AM</span>
                    </div>
                    <p className="text-sm text-text-secondary font-medium">Object 'Footwear' detected with <span className="text-green-600 font-black">99.8% confidence</span>.</p>
                  </div>
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                    <div className="relative flex aspect-video w-full flex-col items-center justify-center overflow-hidden rounded-2xl border border-gray-200 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-gray-50 dark:border-gray-700 dark:bg-gray-900 shadow-inner">
                      <img alt="Isolated sneaker" className="h-4/5 w-auto object-contain drop-shadow-2xl animate-pulse-slow" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCFEJQVuANM72lpBBVl2FtBe_Pd2AflbbvB_TfWKRY_MnW_sCsrMCmY1rSqpNjzL6hELnKRdGXMVA2NuhA9I6FLW-UQJqh18uVBB0xPBeaBmCPwd3q2PzdvkciIboRv0TGDuB77Iboz4BR0EmeWgW91OUBdaJ9T1J7O6jSSdzaisSwD9AhvE5Wdg1DL4en-M23yiy6A5fJdgp7rqt5ZYT3v9wZFqbBBxVnFUrYkZzoVJaF_10oMxX8d5NaJ3Nj4o2muaEa43qmt3n4" />
                      <div className="absolute bottom-3 left-3 rounded-lg bg-black/60 px-3 py-1 text-[10px] font-black text-white backdrop-blur-md uppercase tracking-widest shadow-lg">Mask Preview</div>
                    </div>
                    <div className="flex flex-col justify-center gap-4 rounded-2xl bg-background-light p-6 dark:bg-background-dark/50 border border-gray-50 dark:border-gray-800">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-bold text-text-secondary uppercase tracking-tight">Object Type</span>
                        <span className="text-sm font-black text-text-main dark:text-white">Sneaker / Footwear</span>
                      </div>
                      <div className="h-px w-full bg-gray-200 dark:bg-gray-700/50"></div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-bold text-text-secondary uppercase tracking-tight">Colors Detected</span>
                        <div className="flex gap-2">
                          <div className="size-5 rounded-full border-2 border-white bg-white shadow-md"></div>
                          <div className="size-5 rounded-full border-2 border-white bg-red-500 shadow-md"></div>
                          <div className="size-5 rounded-full border-2 border-white bg-slate-800 shadow-md"></div>
                        </div>
                      </div>
                      <div className="h-px w-full bg-gray-200 dark:bg-gray-700/50"></div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-bold text-text-secondary uppercase tracking-tight">Mask Quality</span>
                        <span className="text-sm font-black text-green-600 dark:text-green-400">High Resolution</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Step 3: Creative Copy Generated */}
              <div className="relative flex gap-6 z-10">
                <div className="flex flex-col items-center">
                  <div className="flex size-10 items-center justify-center rounded-full bg-primary text-text-main shadow-lg ring-4 ring-white dark:ring-surface-dark">
                    <span className="material-symbols-outlined text-[20px] font-black">check</span>
                  </div>
                </div>
                <div className="flex flex-1 flex-col gap-4 pb-4">
                  <div className="flex flex-col">
                    <div className="flex items-baseline justify-between">
                      <h3 className="text-lg font-black text-text-main dark:text-white">Creative Copy Generated</h3>
                      <span className="text-xs font-bold text-text-secondary uppercase">09:05 AM</span>
                    </div>
                    <p className="text-sm text-text-secondary font-medium">Optimized for Instagram and Facebook Ads.</p>
                  </div>
                  <div className="group relative flex flex-col gap-4 rounded-2xl border border-gray-200 bg-background-light p-6 transition-all hover:border-primary/50 hover:shadow-xl dark:border-gray-700 dark:bg-background-dark/50">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-dark dark:text-primary">Ad Copy Variant A</span>
                      <button className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-white dark:hover:bg-slate-700 rounded-lg">
                        <span className="material-symbols-outlined text-text-secondary hover:text-primary text-xl">content_copy</span>
                      </button>
                    </div>
                    <div>
                      <p className="mb-3 text-lg font-black text-text-main dark:text-white leading-tight">"Step into Summer with Unmatched Comfort ☀️👟"</p>
                      <p className="text-sm leading-relaxed text-text-secondary dark:text-gray-300 font-medium italic">
                        Get ready to conquer the heat in style. Our newest Summer Sneaker collection combines breathable mesh technology with iconic design. Lightweight, durable, and ready for your next adventure. Limited stock available! #SummerVibes #SneakerHead
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Step 4: Listing Images Produced */}
              <div className="relative flex gap-6 z-10">
                <div className="flex flex-col items-center">
                  <div className="flex size-10 items-center justify-center rounded-full bg-primary text-text-main shadow-lg ring-4 ring-white dark:ring-surface-dark">
                    <span className="material-symbols-outlined text-[20px] font-black">check</span>
                  </div>
                </div>
                <div className="flex flex-1 flex-col gap-4 pb-4">
                  <div className="flex flex-col">
                    <div className="flex items-baseline justify-between">
                      <h3 className="text-lg font-black text-text-main dark:text-white">Listing Images Produced</h3>
                      <span className="text-xs font-bold text-text-secondary uppercase">09:10 AM</span>
                    </div>
                    <p className="text-sm text-text-secondary font-medium">4 lifestyle variations generated based on <span className="text-primary-dark font-black">#Summer</span> theme.</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                    {[
                      "https://lh3.googleusercontent.com/aida-public/AB6AXuA3_ws_CbO8IEHHhMwK6WSPQYNKdyWsjYB8cBBL8jsr0tGfuh8A6mgISqDXEIKeAyXzPQDFMQbs-KNdOsZXRuGCw3DiN8WvXS6ePIOvAPfh5Inonbnt-e4DeOPNk0F1DzO4hu5aO-JxBLOTShKDlGQWmvxkXn5WdtzVrZkO0EPVDLoYG4sHqPCvGC8sAE8roEQJkEZ8llZoa7ZvIMBHFZ1QLHxbHspN0ovaZzWCZ5_oLfyEoseOZ24vBByMV9TRROVpkG0cxi4oEYc",
                      "https://lh3.googleusercontent.com/aida-public/AB6AXuCem-4DjV5p9E0mD9Rz1AkHC4XL7w3R0uA3IrHvQte3-3b97wq45xBwD8giQ1BKLozUlaOcARbNJr3u_TUnVQH0PqL7hYCYaow89BwF4r6Kl75Cej4jHTRFN-Ur0APDDae_T0-PhaQHjGKyTjOJrpeSGuV8_H5fMwTOeNoEy9pdTqnTJa0JfFBlRc9v9k81LwJfvv8XotymPvg14oM0tyRSK1XZ7YZLaH9wtVzlxoB8ROqHg2CSgO6_-W3GMpw-RyyAUUAbzYzNXlg",
                      "https://lh3.googleusercontent.com/aida-public/AB6AXuB_baRtLGxEi3YNf1GQ2er4KOz8JBE_Dt0ZW83bQPqD1tvPG2RnzWGH5tz7JFe3-VAqGOL7w08uqMez-IkyhUIk83WjMZJjggPin-Utze-4OlEx242NLvJsDN_y2jkTdxkIk0X4HRDF17kzIcCyqg6Vm-zRrXzSX3H6WZHZgAyKOrvig8CpQ_k6x7_DBGV7t7_5eIuQZgxhjP4hRwi3V9_JTfBZ24k-OslQGxvGv87_pkNt2mMoPq502CntsgP1Y8bk7CigJVpkqRk",
                      "https://lh3.googleusercontent.com/aida-public/AB6AXuBDZHrX-bYvHbwladoORy2OIj5cGCBFmuL-lkV_HaYXSimikByFJ_LL3tkaENhz4PsRYH8EcntLCekHTBmR10gRFvJZ3BJrqWYR9OxTrUwdnWY9k6u3Ika-qVX91pS6God7UxbSjlJkDvrPtOnGacEnIOkm84JwkkxqH40WnmeitGEPbzHWr6Kg6efq2XMfMpbwYWW7bFRrcDD8EDRH8XG-6qrYLgwVLg-usOB0FIpr8vXYRQQJwYcc9oFOlx_p27m8DCXNgDPLhhw"
                    ].map((url, i) => (
                      <div key={i} className="group relative aspect-square overflow-hidden rounded-2xl bg-gray-100 dark:bg-gray-800 shadow-sm ring-1 ring-black/5">
                        <div className="absolute inset-0 bg-cover bg-center transition-transform duration-700 group-hover:scale-110" style={{ backgroundImage: `url('${url}')` }}></div>
                        <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 transition-opacity group-hover:opacity-100 backdrop-blur-[1px]">
                          <button className="rounded-full bg-white p-2.5 text-black shadow-2xl hover:bg-primary transition-all scale-75 group-hover:scale-100">
                            <span className="material-symbols-outlined text-[20px] font-bold">zoom_in</span>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Step 5: Video Ad Rendered */}
              <div className="relative flex gap-6 z-10">
                <div className="flex flex-col items-center">
                  <div className="z-10 flex size-10 items-center justify-center rounded-full bg-primary text-text-main shadow-xl ring-4 ring-primary/20 animate-pulse-slow">
                    <span className="material-symbols-outlined text-[20px] font-black">check</span>
                  </div>
                </div>
                <div className="flex flex-1 flex-col gap-4 pb-12">
                  <div className="flex flex-col">
                    <div className="flex items-baseline justify-between">
                      <h3 className="text-lg font-black text-text-main dark:text-white">Video Ad Rendered</h3>
                      <span className="text-xs font-bold text-text-secondary uppercase">09:12 AM</span>
                    </div>
                    <p className="text-sm text-text-secondary font-medium">15s vertical video ready for <span className="font-black text-slate-900 dark:text-white tracking-tight">Reels/TikTok</span>.</p>
                  </div>
                  <div className="relative w-full max-w-sm overflow-hidden rounded-3xl bg-black shadow-2xl group cursor-pointer border-2 border-white dark:border-slate-800">
                    <div className="aspect-[9/16] w-full bg-cover bg-center opacity-90 transition-transform duration-700 group-hover:scale-105" style={{ backgroundImage: `url('https://lh3.googleusercontent.com/aida-public/AB6AXuAVDqAMedkTPWaUibBhC6602bwAxokI9MAJuectd_nN0RoafnvvC1ygW9tq_7TSP1e4mTzK-yMzzWKk9HfUspwX2GXXzQHOd6jt9p_uCAWq8cvMcyERg5VNkxHAyHHerndfBBID4ZOrrxosOzprXTQ6EJV2gtVTiUGEdCWD5zVkpfjb-dDIO8_JXhO91TqiJ_aSTI1pTlG3BWfIMwxjb9heCh1nGaL218Qn6xf3hyskUbBp8TDuSCnb1CCT6ix3mUajQRQUFP4kcZo')` }}></div>
                    <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/30 transition-colors group-hover:bg-black/10">
                      <button className="flex size-20 items-center justify-center rounded-full bg-white/30 text-white backdrop-blur-md transition-all hover:scale-110 hover:bg-white/40 shadow-2xl border border-white/40">
                        <span className="material-symbols-outlined text-[48px]" style={{ fontVariationSettings: "'FILL' 1" }}>play_arrow</span>
                      </button>
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent p-6 pt-12">
                      <p className="text-sm font-black text-white tracking-tight">Summer_Campaign_Reel_v1.mp4</p>
                      <p className="text-[10px] text-gray-300 font-bold uppercase tracking-widest mt-1">00:15 • 1080x1920</p>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>

      <style>{`
        .animate-pulse-slow {
          animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.85; transform: scale(1.05); }
        }
      `}</style>
    </div>
  );
};

export default ProjectTimeline;
