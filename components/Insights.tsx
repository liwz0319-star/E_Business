
import React, { useState } from 'react';

const Insights: React.FC = () => {
  const [timeRange, setTimeRange] = useState('Last 30 Days');

  const handleAction = (label: string) => {
    alert(`Action triggered: ${label}`);
  };

  const topAssets = [
    {
      id: 1,
      name: 'Summer Collection Ad #4',
      created: '2 days ago',
      platform: 'Shopify',
      type: 'Image',
      score: 92,
      img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuC3mRVAZzvTAHUz-Qdpizjvc4EetHN7DIxUez7sz94Hp29ts8dWvNb3C-jVZT6Z4AY_6_DA4aBa7F-pkSM_atNzaThGuD6d67YqdQ33sPha48Sre2KvWLxSn3FykbzMNA8dWUaY-ymkKJ4WWfdKgMm-ZrhrknRuce-Hr4Ursa69uHtoG00Gj6rKTxAXiyl27exd16tN91-TWEwEyKP1KyNSagnujeyw0ClFjxa6EPP596kl6xr8-pqDt8o_nm_F48h6erDMT5K67ps'
    },
    {
      id: 2,
      name: 'Viral Unboxing Hook',
      created: '5 days ago',
      platform: 'TikTok',
      type: 'Video',
      score: 88,
      img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDKv71oLCeBTvMVVHwB12_iwSCuYxZFR99fbOR5nQfuOuVoft1LLpqpr_1mEBHOaEsJZ9z-A_I3KnfwrsJcbtI5tJTCxUQeSJvoOQkkDd1j0d55Mekpak8dT2nhZMOocp--Aeq4nq1oTFCBOjkXNG2MgG1GnxZ8bZyJ5lWHvkdW2nUGhsHWlLO-Ow7RbKuO2q8iFEdiReJuVm-Up7DSuXuKEu_LFfqgxx74siUG7lSXpras6hrvVQy4EgFMBq4tVR21Ph0BWe3N_w8'
    },
    {
      id: 3,
      name: 'SEO Product Description',
      created: '1 week ago',
      platform: 'Amazon',
      type: 'Copy',
      score: 75,
      img: null
    }
  ];

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-background-light dark:bg-background-dark font-inter transition-colors">
      <header className="w-full bg-background-light dark:bg-background-dark py-6 px-8 border-b border-border-light dark:border-border-dark/20 shrink-0 z-10 transition-colors">
        <div className="max-w-7xl mx-auto w-full flex flex-wrap justify-between items-end gap-4">
          <div className="flex flex-col gap-1">
            <h1 className="text-text-main dark:text-white text-3xl font-black tracking-tight">Performance Insights</h1>
            <p className="text-text-muted text-base font-normal">Track the ROI and engagement of your AI-generated assets.</p>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={() => handleAction('Change Time Range')}
              className="flex items-center justify-center rounded-lg h-10 px-4 bg-white dark:bg-[#1e2928] border border-border-light dark:border-border-dark text-text-main dark:text-white text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors shadow-sm"
            >
              <span className="material-symbols-outlined text-[18px] mr-2">calendar_today</span>
              {timeRange}
            </button>
            <button 
              onClick={() => handleAction('Export Report')}
              className="flex items-center justify-center rounded-lg h-10 px-4 bg-primary text-text-main text-sm font-bold shadow-sm hover:bg-primary-dark transition-colors"
            >
              <span className="material-symbols-outlined text-[20px] mr-2">download</span>
              Export Report
            </button>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto sidebar-scroll p-8">
        <div className="max-w-7xl mx-auto w-full flex flex-col gap-8 pb-20">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: 'Total Views', value: '1.2M', trend: '+12%', icon: 'visibility' },
              { label: 'Click-Through Rate', value: '3.8%', trend: '+0.5%', icon: 'ads_click' },
              { label: 'Conversion Rate', value: '2.1%', trend: '+0.1%', icon: 'shopping_cart' },
              { label: 'AI Efficiency Gain', value: '40hrs Saved', trend: 'ROI +200%', icon: 'auto_awesome', highlight: true },
            ].map((stat, i) => (
              <div 
                key={i} 
                onClick={() => handleAction(`View details for ${stat.label}`)}
                className={`flex flex-col gap-3 rounded-xl p-6 border cursor-pointer transition-all hover:shadow-md ${
                  stat.highlight 
                  ? 'bg-primary/10 border-primary shadow-sm ring-1 ring-primary/30' 
                  : 'bg-white dark:bg-[#1e2928] border-border-light dark:border-border-dark shadow-sm'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className={`p-2 rounded-lg ${stat.highlight ? 'bg-primary/20 text-primary-dark' : 'bg-primary/20 text-primary-dark'}`}>
                    <span className="material-symbols-outlined text-[24px]">{stat.icon}</span>
                  </div>
                  <span className={`flex items-center px-2 py-1 rounded-full text-xs font-bold ${
                    stat.highlight 
                    ? 'bg-primary/10 text-primary-dark border border-primary/20' 
                    : 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600'
                  }`}>
                    {!stat.highlight && <span className="material-symbols-outlined text-[14px] mr-1">trending_up</span>}
                    {stat.trend}
                  </span>
                </div>
                <div>
                  <p className="text-text-muted text-sm font-medium">{stat.label}</p>
                  <p className="text-text-main dark:text-white text-2xl font-bold mt-1">{stat.value}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Charts Area */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 flex flex-col bg-white dark:bg-[#1e2928] border border-border-light dark:border-border-dark rounded-xl shadow-sm p-6 transition-colors">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="text-text-main dark:text-white text-lg font-bold">Conversion Trends</h3>
                  <p className="text-text-muted text-sm">AI Content vs. Standard Benchmarks</p>
                </div>
                <div className="flex gap-4 text-sm">
                  <div className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-full bg-primary"></span>
                    <span className="text-text-muted">AI Content</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-full bg-gray-300 dark:bg-gray-600"></span>
                    <span className="text-text-muted">Benchmark</span>
                  </div>
                </div>
              </div>
              <div className="relative w-full h-64 lg:h-80">
                <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 100 50">
                  <line className="text-gray-100 dark:text-gray-800" stroke="currentColor" strokeWidth="0.5" x1="0" x2="100" y1="0" y2="0"></line>
                  <line className="text-gray-100 dark:text-gray-800" stroke="currentColor" strokeWidth="0.5" x1="0" x2="100" y1="12.5" y2="12.5"></line>
                  <line className="text-gray-100 dark:text-gray-800" stroke="currentColor" strokeWidth="0.5" x1="0" x2="100" y1="25" y2="25"></line>
                  <line className="text-gray-100 dark:text-gray-800" stroke="currentColor" strokeWidth="0.5" x1="0" x2="100" y1="37.5" y2="37.5"></line>
                  <line className="text-gray-100 dark:text-gray-800" stroke="currentColor" strokeWidth="0.5" x1="0" x2="100" y1="50" y2="50"></line>
                  
                  <path className="text-gray-300 dark:text-gray-600" d="M0 40 C 10 38, 20 42, 30 35 C 40 32, 50 38, 60 30 C 70 28, 80 32, 90 25 L 100 28" fill="none" stroke="currentColor" strokeDasharray="2,1" strokeLinecap="round" strokeWidth="1.5"></path>
                  <defs>
                    <linearGradient id="chartGradient" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor="#81D8D0" stopOpacity="0.5"></stop>
                      <stop offset="100%" stopColor="#81D8D0" stopOpacity="0"></stop>
                    </linearGradient>
                  </defs>
                  <path d="M0 35 C 10 30, 20 25, 30 28 C 40 20, 50 15, 60 18 C 70 10, 80 12, 90 5 L 100 8 V 50 H 0 Z" fill="url(#chartGradient)"></path>
                  <path d="M0 35 C 10 30, 20 25, 30 28 C 40 20, 50 15, 60 18 C 70 10, 80 12, 90 5 L 100 8" fill="none" stroke="#81D8D0" strokeLinecap="round" strokeWidth="1.5" vectorEffect="non-scaling-stroke"></path>
                  <circle 
                    onClick={() => handleAction('View data point details')}
                    className="fill-white stroke-primary cursor-pointer hover:r-3 transition-all" cx="60" cy="18" r="1.5" strokeWidth="0.5"
                  ></circle>
                </svg>
                <div className="absolute top-[30%] left-[58%] bg-text-main text-white text-[10px] py-1 px-2 rounded pointer-events-none transform -translate-x-1/2 -translate-y-full mb-2 shadow-lg">
                  2.8% Conv
                  <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 rotate-45 w-2 h-2 bg-text-main"></div>
                </div>
              </div>
              <div className="flex justify-between text-xs text-text-muted mt-4 font-medium">
                <span>Week 1</span>
                <span>Week 2</span>
                <span>Week 3</span>
                <span>Week 4</span>
              </div>
            </div>

            <div className="lg:col-span-1 flex flex-col bg-white dark:bg-[#1e2928] border border-border-light dark:border-border-dark rounded-xl shadow-sm p-6 transition-colors">
              <div className="mb-6">
                <h3 className="text-text-main dark:text-white text-lg font-bold">Platform Breakdown</h3>
                <p className="text-text-muted text-sm">Revenue share by channel</p>
              </div>
              <div className="flex-1 flex items-end justify-between gap-2 px-2">
                {[
                  { label: 'Shopify', height: '85%', opacity: 'bg-primary/80' },
                  { label: 'Amazon', height: '65%', opacity: 'bg-primary/60' },
                  { label: 'Insta', height: '45%', opacity: 'bg-primary/40' },
                  { label: 'TikTok', height: '30%', opacity: 'bg-primary/30' },
                ].map((bar, i) => (
                  <div 
                    key={i} 
                    onClick={() => handleAction(`Filter insights by ${bar.label}`)}
                    className="flex flex-col items-center gap-2 group w-1/4 cursor-pointer"
                  >
                    <div className="relative w-full bg-gray-50 dark:bg-gray-800 rounded-t-lg overflow-hidden h-48 flex items-end">
                      <div className={`w-full ${bar.opacity} group-hover:bg-primary transition-all duration-300 rounded-t-lg`} style={{ height: bar.height }}></div>
                    </div>
                    <span className="text-[10px] font-semibold text-text-muted truncate w-full text-center">{bar.label}</span>
                  </div>
                ))}
              </div>
              <div className="mt-6 pt-4 border-t border-border-light dark:border-border-dark flex justify-between items-center">
                <div>
                  <p className="text-text-muted text-[10px]">Top Performer</p>
                  <p className="text-text-main dark:text-white font-bold text-sm">Shopify Store</p>
                </div>
                <div className="text-right">
                  <p className="text-text-muted text-[10px]">Total Sales</p>
                  <p className="text-text-main dark:text-white font-bold text-sm">$12,450</p>
                </div>
              </div>
            </div>
          </div>

          {/* Table Area */}
          <div className="flex flex-col bg-white dark:bg-[#1e2928] border border-border-light dark:border-border-dark rounded-xl shadow-sm overflow-hidden transition-colors">
            <div className="p-6 border-b border-border-light dark:border-border-dark flex justify-between items-center">
              <div>
                <h3 className="text-text-main dark:text-white text-lg font-bold">Top Performing AI Assets</h3>
                <p className="text-text-muted text-sm">Assets with highest engagement this week</p>
              </div>
              <button 
                onClick={() => handleAction('View All Assets')}
                className="text-primary-dark hover:text-primary text-sm font-semibold flex items-center transition-colors"
              >
                View All <span className="material-symbols-outlined text-sm ml-1">arrow_forward</span>
              </button>
            </div>
            <div className="overflow-x-auto no-scrollbar">
              <table className="w-full text-left border-collapse">
                <thead className="bg-gray-50 dark:bg-gray-800/50 text-text-muted text-[10px] uppercase font-bold tracking-wider">
                  <tr>
                    <th className="px-6 py-4">Asset</th>
                    <th className="px-6 py-4">Platform</th>
                    <th className="px-6 py-4">Type</th>
                    <th className="px-6 py-4">Performance Score</th>
                    <th className="px-6 py-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-light dark:divide-border-dark">
                  {topAssets.map((asset) => (
                    <tr key={asset.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className={`h-10 w-10 rounded-lg bg-gray-200 shrink-0 bg-cover bg-center overflow-hidden border border-border-light dark:border-border-dark flex items-center justify-center`} 
                               style={asset.img ? { backgroundImage: `url('${asset.img}')` } : {}}>
                            {!asset.img && <span className="text-text-muted font-bold text-[10px]">COPY</span>}
                          </div>
                          <div className="min-w-0">
                            <p className="text-text-main dark:text-white font-semibold text-sm truncate">{asset.name}</p>
                            <p className="text-text-muted text-[10px]">Created {asset.created}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-[18px] text-text-muted">
                            {asset.platform === 'Shopify' ? 'shopping_bag' : asset.platform === 'TikTok' ? 'play_circle' : asset.platform === 'AI Generated' ? 'auto_awesome' : 'store'}
                          </span>
                          <span className="text-text-main dark:text-white text-sm">{asset.platform}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          asset.type === 'Image' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300' :
                          asset.type === 'Video' ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300' :
                          'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300'
                        }`}>
                          {asset.type}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 overflow-hidden">
                            <div className="bg-primary h-full rounded-full transition-all duration-1000" style={{ width: `${asset.score}%` }}></div>
                          </div>
                          <span className="text-xs font-bold text-text-main dark:text-white">{asset.score}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button 
                          onClick={() => handleAction(`Options for ${asset.name}`)}
                          className="text-text-muted hover:text-primary transition-colors p-1"
                        >
                          <span className="material-symbols-outlined">more_vert</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Insights;
