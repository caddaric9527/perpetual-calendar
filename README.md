# 📅 万年历 · 中外节日日历订阅

一条 iCalendar 订阅链接，把**中国节日与中国法定放假安排** + **欧美日韩 9 国节日**同步到 Apple 日历 / Outlook / Google 日历。订阅一次，往后自动更新，不用再手动导入。

![iCal](https://img.shields.io/badge/iCalendar-RFC%205545-success)
![Apple](https://img.shields.io/badge/Apple%20Calendar-订阅支持-black)
![years](https://img.shields.io/badge/覆盖-2020–2040-blue)
![license](https://img.shields.io/badge/license-MIT-green)

## 呈现口径（关键设计）

| | 中国 | 外国（欧美日韩） |
| --- | --- | --- |
| 节日 | ✅ 农历节日 + 公历纪念日 + 24 节气 | ✅ 全国性公共节日 |
| 放假安排 | ✅ `🏖️ 休` 放假 / `💼 班` 调休上班 | ❌ 不显示 |
| 补休/振替 | 体现在「班」与「休」的调换中 | ❌ 过滤 `振替休日`/`대체공휴일`/`observed` |
| 连休多日 | 逐日一条（便于看清哪些天放假） | 合并一条，注明「连休 N 天」 |

简单说：**中国的日历告诉你哪天不用上班，外国的日历只告诉你哪天过节。**

## 订阅地址

| 日历 | 内容 | 订阅 |
| --- | --- | --- |
| 全部 | 中国 + 9 国，约 3200 条 | `webcal://caddaric9527.github.io/perpetual-calendar/all.ics` |
| 中国 | 农历节日、24 节气、放假与调休 | `webcal://caddaric9527.github.io/perpetual-calendar/cn.ics` |
| 国际 | 9 国节日合计 | `webcal://caddaric9527.github.io/perpetual-calendar/intl.ics` |
| 单国 | `us` `gb` `ca` `au` `sg` `jp` `kr` `de` `fr` | `webcal://caddaric9527.github.io/perpetual-calendar/jp.ics` 等 |

> 网页版一键订阅：<https://caddaric9527.github.io/perpetual-calendar/>
> 客户端只认 `https://` 时，把 `webcal://` 换成 `https://` 即可。

**iPhone / iPad**：点订阅链接 →「订阅」→ 完成；或 设置 → 日历 → 账户 → 添加账户 → 其他 → 添加已订阅的日历。
**Mac**：日历 App → 文件 → 新建日历订阅 → 粘贴链接 → 刷新频率选「每天」。

## 包含内容

**🇨🇳 中国**
- 农历节日：春节、元宵、龙抬头、端午、七夕、中元、中秋、重阳、腊八、小年、除夕（含农历日期与干支生肖年）
- 公历纪念日：元旦、情人节、妇女节、植树节、劳动节、青年节、儿童节、建党节、建军节、教师节、国庆节
- 二十四节气：全年 24 个节气精确到日（清明同时作为节日条目）
- 放假安排：`🏖️ 休 · 春节` / `💼 班 · 春节`，跟随 gov.cn 公告自动同步

**🌍 外国（9 国）**
- 🇺🇸 美国：11 个联邦法定假日
- 🇬🇧 英国：英格兰+威尔士银行假日（不含苏格兰、北爱独有）
- 🇨🇦 加拿大：全国性法定假日
- 🇦🇺 澳大利亚：全国性 + 覆盖 ≥4 个州/领地的节日（如 Anzac Day、King's Birthday）
- 🇸🇬 新加坡：11 个公共假日（含开斋节、哈芝节、卫塞节、屠妖节）
- 🇯🇵 日本：16 个祝日（含春分/秋分，不含振替休日）
- 🇰🇷 韩国：法定公休（설날/추석 连休合并为一条）
- 🇩🇪 德国：9 个全国性法定假日
- 🇫🇷 法国：11 个全国性法定假日

## 本地使用

```bash
pip install -r requirements.txt

python sync_holidays.py       # 中国放假安排 → data/holidays_cn.json
python sync_world.py          # 9 国节日 → data/world/*.json
python selftest.py            # 日期与呈现口径校验
python generate.py            # 生成到 docs/（默认 2020-2040）

python generate.py --from-year 1900 --to-year 2099 --cn-only   # 纯中国万年历
python generate.py --from-year 2024 --to-year 2028 --no-terms
```

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `--from-year` / `--to-year` | 2020 / 2040 | 中国部分支持 1900–2099 |
| `--out` | `docs` | 输出目录 |
| `--site` | 本仓库 Pages 地址 | 写入 `SOURCE` 属性 |
| `--overrides` | `data/holidays_cn.json` | 中国放假安排数据 |
| `--no-terms` | 关闭 | 不包含二十四节气 |
| `--cn-only` | 关闭 | 只生成中国日历，可用 1900–2099 |

## 数据来源

| 数据 | 来源 | 更新方式 |
| --- | --- | --- |
| 中国放假安排（含调休） | gov.cn 公告，经 [holiday-cn](https://github.com/NateScarlet/holiday-cn) 结构化 | `sync_holidays.py`，每周一 CI 自动拉取 |
| 各国公共节日 | [date.nager.at](https://date.nager.at) 免费 API | `sync_world.py`，每周一 CI 自动拉取 |
| 农历 / 干支 / 节气 | [cnlunar](https://github.com/OPN48/cnlunar) + [zhdate](https://github.com/CutePandaSh/zhdate) | 本地计算，1900–2099 |

**为什么外国节日用数据而不是规则算**：日本振替休日、韩国替代公休日、新加坡的开斋节/卫塞节/屠妖节每年由官方公布，规则推算必然出错（伊斯兰历、印度历与公历无固定换算）。用官方结构化数据是唯一可靠做法。

**为什么中国放假安排要单独同步**：同样是行政公告，每年 11 月前后才公布次年安排，无法用算法推。公告发布后，下一个周一的 CI 自动抓到新一年数据并重建，你无需操作。

## 容错设计

- 数据源某年 404（未公布）→ 跳过该年，其他年份照常
- 数据源整体不可用 → **不覆盖**本地文件，继续用上次数据部署
- 同步步骤 `continue-on-error` → 数据源抖动不会阻断日历发布
- 清洗后某国某年为 0 条 → 退回该年全部 Public/Bank 条目，避免静默丢数据

## 工作流

`.github/workflows/build.yml`：

1. 安装依赖
2. `sync_holidays.py` + `sync_world.py` 同步数据（失败不阻断）
3. `selftest.py` 校验（日期错误 / 外国日历混入休班标记 → 构建失败）
4. `generate.py` 生成 12 个 `.ics` 到 `docs/`
5. 变更回写仓库（`[skip ci]` 防循环）
6. `actions/configure-pages` → 上传 → 部署 Pages
7. 每周一自动重跑

## 项目结构

```
calgen/
  ical.py     RFC 5545 生成器（UTF-8 折行 75 字节、全天事件、稳定 UID）
  china.py    农历节日、公历纪念日、二十四节气
  world.py    9 国节日（读 data/world/*.json，只呈现节日本体）
generate.py   CLI：生成 all/cn/intl + 9 个单国 .ics
sync_holidays.py  中国放假安排 → data/holidays_cn.json
sync_world.py     各国公共节日 → data/world/{cc}.json
selftest.py   日期与呈现口径自检
data/         节假日数据缓存（CI 自动回写）
docs/         落地页 + 生成的 .ics（Pages 根目录）
```

## 技术要点

- **稳定 UID**：`{YYYYMMDD}-{slug}@perpetual-calendar`，重新生成不会在客户端产生重复事件
- **全天事件**：`DTSTART;VALUE=DATE` + 次日 `DTEND`，不占用时段（`TRANSP:TRANSPARENT`）
- **自动刷新**：`REFRESH-INTERVAL` / `X-PUBLISHED-TTL: P1D`，Apple 日历每日拉取
- **UTF-8 折行**：按字节切分且不切断多字节字符，中文字段不乱码

## 已知限制

- 英国采用英格兰+威尔士口径；苏格兰（1月2日、St Andrew's Day）、北爱（Orangemen's Day）独有假日不包含
- 澳大利亚州级假日（各州 Labour Day、Melbourne Cup、AFL Grand Final 等）不包含
- 加拿大省假日（Boxing Day、Family Day 等）不包含
- 外国节日按数据源的官方日期呈现；若某年节日落在周末，部分国家会给出补休日，本项目会**过滤补休条目**，因此该年该节日可能显示在补休前的工作日日期上

## License

[MIT](LICENSE)
