import requests
import re
import datetime
from opencc import OpenCC

# 初始化繁簡轉換器
cc = OpenCC('s2t')

# --- 設定區 ---

# 1. 來源列表
SOURCE_URLS = [
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/1300%E4%B8%AA%E7%9B%B4%E6%92%AD%E6%BA%90%E5%85%A8%E9%83%A8%E6%9C%89%E6%95%88%E3%80%90%E5%85%A8%E9%83%A84k%E8%80%81%E7%94%B5%E8%84%91%E5%88%AB%E7%94%A8%E3%80%91.m3u8",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/5000%E4%B8%AA%E7%9B%B4%E6%92%AD%E6%BA%90%E5%85%A8%E9%83%A8%E6%9C%89%E6%95%88.m3u",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E6%88%91%E7%9A%84%E6%92%AD%E6%94%BE%E6%BA%90.m3u8",
    "https://raw.githubusercontent.com/suxuang/myIPTV/refs/heads/main/ipv4.m3u",
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/Guovin/iptv-api/refs/heads/gd/output/result.m3u",
    "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u",
    "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u",
    "https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.m3u",
    "https://iptv-org.github.io/iptv/countries/hk.m3u",
    "https://raw.githubusercontent.com/joevess/IPTV/main/home.m3u8",
    "https://raw.githubusercontent.com/YanG-1989/m3u/main/Gather.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/refs/heads/master/streams/hk.m3u",
    "https://raw.githubusercontent.com/Free-TV/IPTV/refs/heads/master/playlists/playlist_hong_kong.m3u8",
    "https://raw.githubusercontent.com/vbskycn/iptv/refs/heads/master/tv/iptv4.m3u",
    "https://epg.pw/test_channels_hong_kong.m3u",
    "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/cnTV_AutoUpdate.m3u8",
    "https://raw.githubusercontent.com/MercuryZz/IPTVN/refs/heads/Files/GAT.m3u",
    "https://cdn.qd.je/live.m3u"
]

ALL_LIVE_SOURCE = "https://iptv-org.github.io/iptv/index.m3u"
REPLAY_SOURCE = "https://iptv.yang-1989.xyz/playlist.m3u"
REPLAY_GROUPS = {
    "•中國「Relay」": "China Replay",
    "•台灣「Relay」": "Taiwan Replay",
    "•香港「Relay」": "Hong Kong",
}
JAPAN_SOURCE = "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_japan.m3u8"
KOREA_SOURCE = "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_korea.m3u8"
TAIWAN_SOURCE = "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_taiwan.m3u8"
IYOUHUN_SOURCE = "https://www.iyouhun.com/tv/zb"
ALLOWED_COUNTRIES = {"US", "CA", "UK", "GB", "HK", "CN", "TW", "JP", "KR"}
COUNTRIES_SOURCE = "https://iptv-org.github.io/api/countries.json"
EXCLUDED_ENTRY_TERMS = (
    "latin america",
    "french",
    "german",
    "hispanic",
    "latin",
    "espanol",
    "español",
    "czech",
)
EXCLUDED_GROUPS = {"Shop", "Auto"}

# 2. 包含關鍵字 (必須包含這些字才抓取)
KEYWORDS = [
    "ViuTV", "HOY", "RTHK", "Jade", "Pearl", "J2", "J5", "Now", "TVB Plus", "TVBPlus", "TVB+",
    "无线", "無線", "有线", "有線", "翡翠", "明珠", "港台", 
]

# 3. 黑名單關鍵字 (包含這些字的一律丟棄)
BLOCK_KEYWORDS = [
    # 來自你的日誌分析 (美國/英語台)
    "FOX", "Pluto", "Local", "NBC", "CBS", "ABC", "AXS", "Snowy", 
    "Reuters", "Mirror", "ET Now", "The Now", "Right Now", "News Now",
    "Chopper", "Wow", "UHD", "8K", "Career", "Comics", "Movies",
    "CBTV",
    
    # 來自你的日誌分析 (大陸/澳門台)
    "浙江", "杭州", "西湖", "廣東", "珠江", "大灣區", # 排除 "杭州西湖明珠"
    "澳門", "Macau", "有線 CH", "互動新聞",           # 排除澳門有線
    "CCTV", "CGTN", "鳳凰", "凤凰", "華麗", "星河", "延时", "測試", "iHOY", "福建"
]

# 4. 【已更新】頻道排序優先級 (越上面越靠前)
ORDER_KEYWORDS = [
    "翡翠", "無線新聞", "明珠", "J2", "J5", "財經",  # TVB系列
    "ViuTV", "Viutv", "VIUTV", "ViuTV 6", "ViuTVsix",  # Viu系列 (包含你加入的大小寫變體)
    "HOY", "奇妙", "有線",                         # HOY/Cable系列
    "港台電視31", "RTHK 31",                      # RTHK系列
    "港台電視32", "RTHK 32",
    "Now新聞", "Now直播"                          # Now系列
]

# 5. 必備的官方/穩定源
STATIC_CHANNELS = [
    {"name": "港台電視31 (官方)", "url": "https://rthklive1-lh.akamaihd.net/i/rthk31_1@167495/index_2052_av-b.m3u8"},
    {"name": "港台電視32 (官方)", "url": "https://rthklive2-lh.akamaihd.net/i/rthk32_1@168450/index_2052_av-b.m3u8"}
]

# --- 邏輯區 ---

def check_url(url):
    """檢測鏈接是否有效 (超時 2 秒)"""
    try:
        response = requests.get(url, timeout=2, stream=True)
        return response.status_code == 200
    except:
        return False

def get_sort_key(item):
    name = item["name"]
    return (0 if re.search(r'[\u4e00-\u9fff]', name) else 1, name.casefold())

def sort_m3u_entries(content):
    header = []
    entries = []
    current_entry = None

    for line in content.splitlines():
        if line.startswith("#EXTINF"):
            if current_entry:
                entries.append(current_entry)
            current_entry = [line]
        elif current_entry:
            current_entry.append(line)
        else:
            header.append(line)

    if current_entry:
        entries.append(current_entry)

    entries.sort(key=lambda entry: get_sort_key({"name": entry[0].split(",", 1)[-1]}))
    return "\n".join(header + [line for entry in entries for line in entry])

def get_m3u_entries(content):
    entries = []
    current_entry = None

    for line in content.splitlines():
        if line.startswith("#EXTINF"):
            if current_entry:
                entries.append(current_entry)
            current_entry = [line]
        elif current_entry:
            current_entry.append(line)

    if current_entry:
        entries.append(current_entry)
    return entries

def get_excluded_feed_countries():
    try:
        response = requests.get(COUNTRIES_SOURCE, timeout=60)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️ 無法讀取國家資料: {e}", flush=True)
        return set()

    return {
        country["name"].casefold()
        for country in response.json()
        if country["code"] not in ALLOWED_COUNTRIES
    }

def is_allowed_country_entry(entry, excluded_feed_countries):
    metadata = entry[0]
    tvg_id = re.search(r'tvg-id="([^"]+)"', metadata)
    if tvg_id:
        tvg_id_value = tvg_id.group(1)
        feed_country = tvg_id_value.partition("@")[2].casefold()
        if feed_country in excluded_feed_countries:
            return False

        country = re.search(r'\.([a-z]{2})(?:@|$)', tvg_id_value, re.IGNORECASE)
        if country and country.group(1).upper() in ALLOWED_COUNTRIES:
            return True

    tvg_country = re.search(r'tvg-country="([^"]+)"', metadata)
    return bool(tvg_country and tvg_country.group(1).upper() in ALLOWED_COUNTRIES)

def filter_allowed_country_entries(content):
    lines = content.splitlines()
    first_entry = next(
        (index for index, line in enumerate(lines) if line.startswith("#EXTINF")),
        len(lines),
    )
    header = lines[:first_entry]
    excluded_feed_countries = get_excluded_feed_countries()
    entries = [
        entry
        for entry in get_m3u_entries(content)
        if is_allowed_country_entry(entry, excluded_feed_countries)
    ]
    print(f"🌎 保留 {len(entries)} 個指定國家頻道。", flush=True)
    return "\n".join(header + [line for entry in entries for line in entry])

def filter_unwanted_entries(content):
    lines = content.splitlines()
    first_entry = next(
        (index for index, line in enumerate(lines) if line.startswith("#EXTINF")),
        len(lines),
    )
    header = lines[:first_entry]
    entries = []
    for entry in get_m3u_entries(content):
        group = re.search(r'group-title="([^"]*)"', entry[0])
        metadata = entry[0].casefold()
        if group and group.group(1) in EXCLUDED_GROUPS:
            continue
        if any(term in metadata for term in EXCLUDED_ENTRY_TERMS):
            continue
        entries.append(entry)

    print(f"🧹 篩選後保留 {len(entries)} 個頻道。", flush=True)
    return "\n".join(header + [line for entry in entries for line in entry])

def set_group_title(line, group_name):
    group = re.search(r'group-title="([^"]*)"', line)
    if group:
        return f'{line[:group.start()]}group-title="{group_name}"{line[group.end():]}'
    return line.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{group_name}"', 1)

def set_group_for_url(content, url, group_name):
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != url:
            continue
        for entry_index in range(index - 1, -1, -1):
            if lines[entry_index].startswith("#EXTINF"):
                lines[entry_index] = set_group_title(lines[entry_index], group_name)
                return "\n".join(lines)
    return content

def get_replay_entries(existing_urls):
    try:
        response = requests.get(REPLAY_SOURCE, timeout=60)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️ 無法更新 Replay 清單: {e}", flush=True)
        return []

    entries = []
    for entry in get_m3u_entries(response.text):
        group = re.search(r'group-title="([^"]*)"', entry[0])
        if not group or group.group(1) not in REPLAY_GROUPS:
            continue

        urls = [line.strip() for line in entry if line.strip().startswith("http")]
        if not urls or any(url in existing_urls for url in urls):
            continue

        entry[0] = (
            f'{entry[0][:group.start()]}group-title="{REPLAY_GROUPS[group.group(1)]}"'
            f'{entry[0][group.end():]}'
        )
        entries.append(entry)
        existing_urls.update(urls)

    print(f"🔁 已加入 {len(entries)} 個 Replay 頻道。", flush=True)
    return entries

def get_country_entries(source, country, existing_urls):
    try:
        response = requests.get(source, timeout=60)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️ 無法更新 {country} 清單: {e}", flush=True)
        return [], []

    entries = []
    existing_japan_urls = []
    for entry in get_m3u_entries(response.text):
        urls = [line.strip() for line in entry if line.strip().startswith("http")]
        if not urls:
            continue

        if any(url in existing_urls for url in urls):
            existing_japan_urls.extend(urls)
            continue

        entry[0] = set_group_title(entry[0], country)
        entries.append(entry)
        existing_urls.update(urls)

    print(
        f"🌐 已加入 {len(entries)} 個 {country} 頻道，重新分類 {len(existing_japan_urls)} 個既有頻道。",
        flush=True,
    )
    return entries, existing_japan_urls

def get_iyouhun_hong_kong_entries(existing_urls):
    try:
        response = requests.get(IYOUHUN_SOURCE, timeout=60)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️ 無法更新游魂港澳台清單: {e}", flush=True)
        return []

    entries = []
    group = None
    for line in response.text.splitlines():
        name, separator, url = line.strip().partition(",")
        if not separator:
            continue
        if url == "#genre#":
            group = name
            continue
        if group != "💓港澳台📶" or not url.startswith("http") or url in existing_urls:
            continue

        entries.append([
            f'#EXTINF:-1 group-title="Hong Kong",{name}',
            url,
        ])
        existing_urls.add(url)

    print(f"🇭🇰 已加入 {len(entries)} 個游魂港澳台頻道。", flush=True)
    return entries

def fetch_and_parse():
    found_channels = []
    
    print("🚀 任務開始！正在抓取網路源...", flush=True)
    
    for index, source in enumerate(SOURCE_URLS):
        print(f"  [{index+1}/{len(SOURCE_URLS)}] 正在讀取: {source}", flush=True)
        try:
            r = requests.get(source, timeout=15)
            r.encoding = 'utf-8'
            
            if r.status_code != 200:
                print(f"    ⚠️ 無法讀取 (Status: {r.status_code})", flush=True)
                continue
            
            lines = r.text.split('\n')
            current_name = ""
            count_added = 0
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                if line.startswith("#EXTINF"):
                    match = re.search(r',(.+)$', line)
                    if match:
                        raw_name = match.group(1).strip()
                        # 轉繁體
                        converted_name = cc.convert(raw_name)
                        # 修正「臺」為「台」
                        current_name = converted_name.replace('臺', '台')
                        
                elif line.startswith("http") and current_name:
                    # 1. 黑名單檢查
                    if any(b.lower() in current_name.lower() for b in BLOCK_KEYWORDS):
                        current_name = ""
                        continue

                    # 2. 白名單檢查
                    if any(cc.convert(k).replace('臺', '台').lower() in current_name.lower() for k in KEYWORDS):
                        # 去重
                        if not any(c['url'] == line for c in found_channels):
                            found_channels.append({"name": current_name, "url": line})
                            count_added += 1
                    current_name = "" # 重置
            
            print(f"    ✅ 抓取成功，新增 {count_added} 個頻道", flush=True)
            
        except Exception as e:
            print(f"    ❌ 抓取錯誤: {e}", flush=True)

    return found_channels

def generate_m3u(channels):
    total = len(channels)
    print(f"\n🔍 共找到 {total} 個潛在頻道，開始檢測有效性...", flush=True)
    
    final_list = []
    
    # 1. 加入靜態源
    for static in STATIC_CHANNELS:
        final_list.append(static)
        
    # 2. 檢測網路源
    for i, ch in enumerate(channels):
        print(f"[{i+1}/{total}] 檢測: {ch['name']} ...", end=" ", flush=True)
        
        if check_url(ch['url']):
            final_list.append(ch)
            print("🟢 有效", flush=True)
        else:
            print("🔴 失效", flush=True)

    # 3. 排序
    print("\n🔄 正在進行排序...", flush=True)
    final_list.sort(key=get_sort_key)

    # 4. 寫入文件
    content = '#EXTM3U x-tvg-url="https://epg.112114.xyz/pp.xml"\n'
    content += f'# Update: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
    
    for item in final_list:
        final_name = item["name"].replace('臺', '台')
        content += f'#EXTINF:-1 group-title="Hong Kong" logo="https://epg.112114.xyz/logo/{final_name}.png",{final_name}\n'
        content += f'{item["url"]}\n'

    with open("hk_live.m3u", "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n🎉 全部完成！共收錄 {len(final_list)} 個有效頻道。", flush=True)
    return final_list

def normalize_group(line):
    group = re.search(r'group-title="([^"]*)"', line)
    if not group:
        return line

    categories = group.group(1).split(";")
    return f'{line[:group.start()]}group-title="{categories[0]}"{line[group.end():]}'

def generate_all_m3u(hk_channels):
    print("\n🌍 正在更新全球頻道清單...", flush=True)
    try:
        response = requests.get(ALL_LIVE_SOURCE, timeout=60)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️ 無法更新全球清單: {e}", flush=True)
        return

    global_lines = [
        normalize_group(line)
        for line in response.text.rstrip().splitlines()
    ]
    global_content = filter_allowed_country_entries("\n".join(global_lines))
    global_lines = global_content.splitlines()
    existing_urls = {
        line.strip() for line in global_content.splitlines()
        if line.strip().startswith("http")
    }
    additions = []

    for channel in hk_channels:
        if channel["url"] not in existing_urls:
            additions.append(channel)
            existing_urls.add(channel["url"])

    extra_entries = []
    for channel in additions:
        name = channel["name"].replace('臺', '台')
        extra_entries.append([
            f'#EXTINF:-1 group-title="Hong Kong",{name}',
            channel["url"],
        ])

    extra_entries.extend(get_replay_entries(existing_urls))
    japan_entries, existing_japan_urls = get_country_entries(JAPAN_SOURCE, "Japan", existing_urls)
    korea_entries, existing_korea_urls = get_country_entries(KOREA_SOURCE, "Korea", existing_urls)
    taiwan_entries, existing_taiwan_urls = get_country_entries(TAIWAN_SOURCE, "Taiwan", existing_urls)
    extra_entries.extend(japan_entries)
    extra_entries.extend(korea_entries)
    extra_entries.extend(taiwan_entries)
    extra_entries.extend(get_iyouhun_hong_kong_entries(existing_urls))

    if extra_entries:
        extra_content = "# Added from hk_live.m3u and Yang replay source\n"
        for entry in extra_entries:
            extra_content += "\n".join(entry) + "\n"
        global_content = f"{global_lines[0]}\n{extra_content}" + "\n".join(global_lines[1:])

    for url in existing_japan_urls:
        global_content = set_group_for_url(global_content, url, "Japan")
    for url in existing_korea_urls:
        global_content = set_group_for_url(global_content, url, "Korea")
    for url in existing_taiwan_urls:
        global_content = set_group_for_url(global_content, url, "Taiwan")

    global_content = global_content.replace('group-title="Taiwan Replay"', 'group-title="Taiwan"')
    global_content = filter_unwanted_entries(global_content)
    global_content = sort_m3u_entries(global_content)

    with open("all_live.m3u", "w", encoding="utf-8") as f:
        f.write(global_content + "\n")

    print(f"🌍 全球清單已更新，加入 {len(additions)} 個香港頻道。", flush=True)

if __name__ == "__main__":
    candidates = fetch_and_parse()
    channels = generate_m3u(candidates)
    generate_all_m3u(channels)
