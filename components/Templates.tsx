
import React, { useState, useMemo } from 'react';

interface TemplatesProps {
  onAssetClick?: (asset: any) => void;
}

const Templates: React.FC<TemplatesProps> = ({ onAssetClick }) => {
  const [activeCategory, setActiveCategory] = useState("All Templates");
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('Recommended');

  const categories = [
    { name: "All Templates" },
    { name: "Beauty & Skincare" },
    { name: "Digital & Tech" },
    { name: "Fashion & Apparel" },
    { name: "Home Decor" }
  ];

  const templates = useMemo(() => [
    {
      title: "Product Teaser - Viral",
      category: "Fashion & Apparel",
      tags: ["Reels", "TikTok"],
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuAE69hLxboFK2IhbRA-JLBTNS4F6VSOXb73rePRq_BsVLcL34NICkkphV4WGOnif3yrXkny2bM16UIzJTG9FUDbw59C6-gziKSEK9GGD-2tS4G3yS0TxfCjW_GKwQWV30LMohdrmd9S9rV4W5aUNUWuuAg2TOwybNi7x8lw7xdRoekhWeEFTkFQLkPE2cr8gM3wE-HbOmDjrcfAyvOHdz65J4-VT-xdRAhMq-sxvLMcwqH3EIEr5-qbNNmQIR9xKntfAf5-pMjoE4A",
      type: "video",
      duration: "0:15"
    },
    {
      title: "Hydra Glow Serum",
      category: "Beauty & Skincare",
      tags: ["Instagram Story", "Product Page"],
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuCusrk-fGSMOjIPLv34G4cc0vDlzaFYmWwsg4ur48BogIpoXFLvKoblZ-EGLU_qiqf7IhX6PFzvCx55tbvl3qmuNZ7ugm5o6zszwhgYwJpT15udjk6sAdmE-ga2u3vx_4aclx42x02-AlUvt9pGOjmyLGnmqD78qd_-so56dKurxqwdusPsRyvi6BuxQJPhtlPBjaL7I0T8rtaAvWF6uxQRuSzJkgWmYYQecC17Xg5U51TMaSr4KTXVUJ0zs2fKIwn34XS96gZ0t4M"
    },
    {
      title: "Flagship Launch Dark",
      category: "Digital & Tech",
      tags: ["Landing Page"],
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuCT9iqfa2hbwC4WIT1n7QrdYJ9oHwBULBUIr2u5h8EldkuvGmKjHakdaFebp8ANis0Y-qFNvE0O1iheSGWbDoJOhRL52TlL9nFpvgVoI3cj3GtkQT4XyXMMDU7lIuCdfVHvfTnQX--WVJLgsHP35PhrBHdvvJ0Rmsclyy4YwL3nfEm6Q1jJkRXummSEcWqOjGmkPgdb6obBNoZ0IqyBUhZo6rsO4tfzCOK0VyXj4yBNi1xDa8m7Fx9t6EyxrxZE3bycPv7SNuh8Y8U"
    },
    {
      title: "Summer Lifestyle",
      category: "Fashion & Apparel",
      tags: ["Lookbook", "Social"],
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuBWjjvXlaGYvDwvmzGdBlA0kQu-3OZXeGqAtz8bLeIine_zqSauTimARj6dY-rMUBpbQJ9IbTqCk_KI_Rf-c6Y574QIdLrd9FxiAW1jCotRR3Uat0a12Rp2oQVS4gykzaXICf0chMiRqA-9UZYMcguy56vv81KzGrJshtbdjaNtBHnLF6-qJtaDviPRSoNj6qDY2_2nPoKQ_TgenOXY2q3TbPbaMfmbd9EYCW1vKmgqAD5cfstYlmH5wM1s_ihgX2OArgX86LTAIRk"
    },
    {
      title: "Modern Living Setup",
      category: "Home Decor",
      tags: ["Catalog"],
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuD3BGUBPEM617FUdSRWjDCD8FDFwp_hf5KbIAfcc4tj20y4kbCozEt1dcZxUGG1mN166wM4nSO7HCf-Q2-5xc9DebjBzubfQElXa3YDAAc5FyErqAW_oGW3UTES7pSysoDgwoG5bubr4Uja9_IPHXfUX-Zy4GOpuJDn0E5C03OKK9zzVp50uHiLXxedEufgIzSn8z8v_Z7wWWIHWQW0cS0ACnRosoHqYSZRW53zqwsaJbTK8Fl_HjVlnbMMZAvCuvFU_1uoFdqRJ-s"
    },
    {
      title: "Wearable Tech Detail",
      category: "Digital & Tech",
      tags: ["Ads"],
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuCFViy_ioRE6xLNCxTT4v7krIyANixA5dSsDWXK1uaJI6lM5h8PuSIrJfAEDX8pMlfAKhLC55uGBf-Gm9xz_6oSL8RKpD7dB1G_IbDeHFx26G_sAmxWBum1jQ86hzcj3ASLbmwndIXfn9ZNY-tUrUsgBUdhjWGvklYcyniZ5DrpkKBuce2xZFFkuoQQrrxcJ4qjIomjN6CcvpRaiMc8W8PEDDoYT9A5_zFpTgA-Kv03CONsQGV0eFB4eqwod41eTf3R2P_qFwK00Jk"
    },
    {
      title: "Botanical Essence",
      category: "Beauty & Skincare",
      tags: ["Social Story"],
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuC2r1Xn8VD9oN-ddKXW9RyNjr9_5XTiMwWfUAwepLX91eBSd6eD2JmK2_tlZUgSqWncqMrzpCdAERtV9OhdbS6ph2xW0ngObyzaQsxqfkdYiPHHM4ZBDsAgBMCM34LG9qoW0ct3HKP2LkCs7Dpeo0-HfpR7BSlYgWxsTKYDh7-W2gYEAHRojoDuRpOMzpJvc9HTgxTeKI4NADS5lbVcOvxVkfbav_7vw4BsEkYPBQoL1QYgvUVcMSoUuOmKu830SmuAJxV3NTG7TVs"
    },
    {
      title: "Streetwear Drop",
      category: "Fashion & Apparel",
      tags: ["Instagram Post"],
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuDF79tqbvs7Q5vn1f8LQ3waRWIYhvpLpz_zZZtUGE9csbB4wyxXN8Nuxn25Np9z2mUYXTsho6E21m8GybFi9gq_C9ODTEaee6C_weNXAXmyCY-muCJ0jveomMdeEio5pZK0Sagq8olSj_Pdeu7fi1gYzpXSDtfQ0BffzkBhE_1dNFKIoUkWQPLs_SLA7inxJwNI4fkzNXTcMgX8gdjk9oNQTF1MbXweD1uA7T07eJGxuAYiWpBOdk7kQxv21SAN8HIP2nWbRtY_E6w"
    }
  ], []);

  const filteredTemplates = useMemo(() => {
    return templates.filter(tpl => {
      const matchesCategory = activeCategory === "All Templates" || tpl.category === activeCategory;
      const matchesSearch = tpl.title.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  }, [activeCategory, searchQuery, templates]);

  const handleUseTemplate = (e: React.MouseEvent, title: string) => {
    e.stopPropagation();
    alert(`Using template: ${title}. Preparing workspace...`);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-background-light dark:bg-background-dark font-inter overflow-hidden">
      <header className="flex flex-col gap-6 px-8 py-6 bg-background-light/90 dark:bg-background-dark/90 backdrop-blur-md z-10 sticky top-0 border-b border-border-light/50 dark:border-border-dark/50 transition-colors">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 max-w-[1400px] mx-auto w-full">
          <div className="flex flex-col gap-1">
            <h1 className="text-3xl font-black tracking-tight text-[#101918] dark:text-white">Template Library</h1>
            <p className="text-[#5b8b86] dark:text-[#9ab6b3] text-sm md:text-base">Discover high-converting layouts for your product catalog.</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative group min-w-[240px]">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <span className="material-symbols-outlined text-[#5b8b86] group-focus-within:text-primary transition-colors" style={{ fontSize: '20px' }}>search</span>
              </div>
              <input 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="block w-full pl-10 pr-3 py-2.5 border-none rounded-xl bg-white dark:bg-[#1e2928] text-sm placeholder-[#5b8b86] shadow-sm ring-1 ring-black/5 focus:ring-2 focus:ring-primary focus:outline-none transition-all dark:text-white" 
                placeholder="Search templates..." 
                type="text"
              />
            </div>
            <div className="relative min-w-[160px]">
              <select 
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="block w-full pl-3 pr-10 py-2.5 border-none rounded-xl bg-white dark:bg-[#1e2928] text-sm text-[#101918] dark:text-white shadow-sm ring-1 ring-black/5 focus:ring-2 focus:ring-primary focus:outline-none appearance-none cursor-pointer hover:bg-gray-50 dark:hover:bg-[#253533] transition-colors"
              >
                <option>Recommended</option>
                <option>Newest First</option>
                <option>Most Popular</option>
              </select>
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <span className="material-symbols-outlined text-[#5b8b86]" style={{ fontSize: '20px' }}>expand_more</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-8 border-b border-[#d4e3e1] dark:border-[#2a3836] overflow-x-auto no-scrollbar max-w-[1400px] mx-auto w-full">
          {categories.map((cat, i) => (
            <button 
              key={i}
              onClick={() => setActiveCategory(cat.name)}
              className={`pb-3 border-b-[3px] text-sm whitespace-nowrap transition-all active:scale-95 ${
                activeCategory === cat.name 
                ? 'border-primary text-[#101918] dark:text-white font-bold' 
                : 'border-transparent text-[#5b8b86] dark:text-[#9ab6b3] hover:text-[#101918] dark:hover:text-white font-medium'
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-8 pt-4 sidebar-scroll">
        <div className="max-w-[1400px] mx-auto">
          {filteredTemplates.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-12">
              {filteredTemplates.map((tpl, i) => (
                <div 
                  key={i} 
                  onClick={() => onAssetClick?.({ title: tpl.title, url: tpl.image, type: tpl.type || 'template', duration: tpl.duration })}
                  className="group relative flex flex-col gap-3 rounded-2xl bg-white dark:bg-[#1e2928] p-3 shadow-sm hover:shadow-lg transition-all duration-300 ring-1 ring-black/5 dark:ring-white/5 cursor-pointer"
                >
                  <div className="relative aspect-[4/5] w-full overflow-hidden rounded-xl bg-gray-100">
                    <div 
                      className="absolute inset-0 bg-cover bg-center transition-transform duration-500 group-hover:scale-105" 
                      style={{ backgroundImage: `url('${tpl.image}')` }}
                    ></div>
                    <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center backdrop-blur-[2px]">
                      <button 
                        onClick={(e) => handleUseTemplate(e, tpl.title)}
                        className="bg-primary hover:bg-[#6ecbc3] text-[#101918] font-semibold py-2.5 px-6 rounded-full transform translate-y-4 group-hover:translate-y-0 transition-all duration-300 shadow-lg flex items-center gap-2 active:scale-95"
                      >
                        <span>Use Template</span>
                        <span className="material-symbols-outlined text-sm font-bold">arrow_forward</span>
                      </button>
                    </div>
                    {tpl.type === 'video' && (
                      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <span className="material-symbols-outlined text-white text-5xl opacity-80">play_circle</span>
                      </div>
                    )}
                    <div className="absolute top-3 left-3 bg-white/90 dark:bg-black/60 backdrop-blur text-xs font-semibold px-2 py-1 rounded text-[#101918] dark:text-white">
                      {tpl.category.split(' ')[0]}
                    </div>
                  </div>
                  <div className="px-1 pb-1">
                    <h3 className="text-base font-bold text-[#101918] dark:text-white leading-tight">{tpl.title}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      {tpl.tags.map((tag, j) => (
                        <span key={j} className="text-xs text-[#5b8b86] dark:text-[#9ab6b3] bg-background-light dark:bg-[#2a3836] px-2 py-0.5 rounded">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-32 text-center">
              <span className="material-symbols-outlined text-6xl text-gray-300 mb-4">search_off</span>
              <h3 className="text-xl font-bold text-gray-400">No templates found</h3>
              <p className="text-gray-400">Try adjusting your category or search term.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Templates;
