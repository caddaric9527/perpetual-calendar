# 📅 万年历 · 中国节假日 + 全球通用节日

一条 iCalendar 订阅链接，把**中国节日与中国法定放假安排**、**二十四节气**，以及**联合国核心国际日 + 全球通行民间节日**同步到 Apple 日历 / Outlook / Google 日历。订阅一次，往后自动更新，不用再手动导入。

![iCal](https://img.shields.io/badge/iCalendar-RFC%205545-success)
![Apple](https://img.shields.io/badge/Apple%20Calendar-订阅支持-black)
![years](https://img.shields.io/badge/覆盖-2020–2040-blue)
![license](https://img.shields.io/badge/license-MIT-green)

## 呈现口径（关键设计）

| | 🇨🇳 中国 | 🌍 全球通用 |
| --- | --- | --- |
| 内容 | 农历节日 + 公历纪念日 + 24 节气 | 联合国核心国际日 + 全球通行民间节日 |
| 放假安排 | ✅ `🏖️ 休` 放假 / `💼 班` 调休上班 | ❌ 不含任何国家的休息日 |
| 数据来源 | gov.cn 国务院公告（行政公告，需同步） | 固定日期 + 浮动规则（纯推算，不依赖外部 API） |
| 每年条数 | 约 60 条（含 24 节气与逐日休/班） | 恒定 28 条 |

简单说：**中国部分告诉你哪天不用上班，全球部分告诉你今天是什么日子。**

## 订阅地址

| 日历 | 内容 | 订阅 |
| --- | --- | --- |
| 全部 | 中国 + 全球，约 1820 条 | `webcal://caddaric9527.github.io/perpetual-calendar/all.ics` |
| 中国 | 农历节日、24 节气、放假与调休（1255 条） | `webcal://caddaric9527.github.io/perpetual-calendar/cn.ics` |
| 全球通用 | 28 个节日 × 21 年（588 条） | `webcal://caddaric9527.github.io/perpetual-calendar/intl.ics` |

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

**🌍 全球通用（28 个）**

*国际纪念日 19 个（联合国官方设立）*

| 日期 | 名称 | 日期 | 名称 |
| --- | --- | --- | --- |
| 3/15 | 国际消费者权益日 | 8/19 | 世界人道主义日 |
| 3/20 | 国际幸福日 | 9/21 | 国际和平日 |
| 3/21 | 世界森林日 | 9/27 | 世界旅游日 |
| 3/22 | 世界水日 | 10/5 | 世界教师日 |
| 3/23 | 世界气象日 | 10/10 | 世界精神卫生日 |
| 4/7 | 世界卫生日 | 10/16 | 世界粮食日 |
| 4/22 | 世界地球日 | 10/24 | 联合国日 |
| 4/23 | 世界读书日 | 12/1 | 世界艾滋病日 |
| 6/5 | 世界环境日 | 12/10 | 世界人权日 |
| 8/12 | 国际青年日 | | |

*民间节日 9 个（全球通行）*

| 日期 | 名称 | 规则 |
| --- | --- | --- |
| 2/14 | 情人节 | 固定 |
| 4/1 | 愚人节 | 固定 |
| 5 月第 2 个周日 | 母亲节 | 浮动 |
| 6 月第 3 个周日 | 父亲节 | 浮动 |
| 10/31 | 万圣节 | 固定 |
| 11 月第 4 个周四 | 感恩节 | 浮动 |
| 春分月圆后首个周日 | 复活节 | 浮动（computus） |
| 12/24 | 平安夜 | 固定 |
| 12/25 | 圣诞节 | 固定 |

> 与中国日历重叠的节日（元旦、妇女节、劳动节、儿童节）只在 `cn.ics` 出现，避免 `all.ics` 里同一天出现两条同名事件。

## 本地使用

```bash
pip install -r requirements.txt

python sync_holidays.py       # 中国放假安排 → data/holidays_cn.json
python selftest.py            # 日期与呈现口径校验（40+ 条断言）
python generate.py            # 生成到 docs/（默认 2020-2040）

python generate.py --from-year 1900 --to-year 2099 --cn-only   # 纯中国万年历
python generate.py --no-intl                                    # 只要中国部分
python generate.py --from-year 2024 --to-year 2028 --no-terms
```

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `--from-year` / `--to-year` | 2020 / 2040 | 中国部分支持 1900–2099 |
| `--out` | `docs` | 输出目录 |
| `--site` | 本仓库 Pages 地址 | 写入 `SOURCE` 属性 |
| `--overrides` | `data/holidays_cn.json` | 中国放假安排数据 |
| `--no-terms` | 关闭 | 不包含二十四节气 |
| `--no-intl` | 关闭 | 不包含全球通用节日 |
| `--cn-only` | 关闭 | 只生成中国日历，可用 1900–2099 |

## 数据来源

| 数据 | 来源 | 更新方式 |
| --- | --- | --- |
| 中国放假安排（含调休） | gov.cn 公告，经 [holiday-cn](https://github.com/NateScarlet/holiday-cn) 结构化 | `sync_holidays.py`，每周一 CI 自动拉取 |
| 全球通用节日 | [un.org 国际日](https://www.un.org/zh/observances) + 人工整理的民间节日规则 | `data/intl_days.json`，纯本地推算 |
| 农历 / 干支 / 节气 | [cnlunar](https://github.com/OPN48/cnlunar) + [zhdate](https://github.com/CutePandaSh/zhdate) | 本地计算，1900–2099 |

**为什么中国放假安排要单独同步**：每年 11 月前后国务院才公布次年安排，且调休是行政决定，无法用算法推。公告发布后，下一个周一的 CI 自动抓到新一年数据并重建，你无需操作。

**为什么全球节日不用外部 API**：全部是固定日期或可算的浮动规则（第 N 个某周日、复活节 computus），本地推算即可，不会因为第三方接口下线、改结构或限流而失效。

## 容错设计

- 数据源某年 404（未公布）→ 跳过该年，其他年份照常
- 数据源整体不可用 → **不覆盖**本地文件，继续用上次数据部署
- 同步步骤 `continue-on-error` → 数据源抖动不会阻断日历发布
- 自检不含外部网络请求 → CI 校验结果只取决于本地代码与数据

## 工作流

`.github/workflows/build.yml`：

1. 安装依赖
2. `sync_holidays.py` 同步中国放假安排（失败不阻断）
3. `selftest.py` 校验（农历/节气/全球节日规则，任一失败则构建失败）
4. `generate.py` 生成 3 个 `.ics` 到 `docs/`
5. 变更回写仓库（`[skip ci]` 防循环）
6. `actions/configure-pages` → 上传 → 部署 Pages
7. 每周一自动重跑

## 项目结构

```
calgen/
  ical.py     RFC 5545 生成器（UTF-8 折行 75 字节、全天事件、稳定 UID）
  china.py    农历节日、公历纪念日、二十四节气
  intl.py     全球通用节日（读 data/intl_days.json，纯规则推算）
generate.py   CLI：生成 all / cn / intl 三个 .ics
sync_holidays.py  中国放假安排 → data/holidays_cn.json
selftest.py   日期与呈现口径自检
data/         holidays_cn.json（CI 回写）+ intl_days.json（人工维护）
docs/         落地页 + 生成的 .ics（Pages 根目录）
```

## 技术要点

- **稳定 UID**：`{YYYYMMDD}-{slug}@perpetual-calendar`，重新生成不会在客户端产生重复事件
- **全天事件**：`DTSTART;VALUE=DATE` + 次日 `DTEND`，不占用时段（`TRANSP:TRANSPARENT`）
- **自动刷新**：`REFRESH-INTERVAL` / `X-PUBLISHED-TTL: P1D`，Apple 日历每日拉取
- **UTF-8 折行**：按字节切分且不切断多字节字符，中文字段不乱码
- **复活节算法**：Anonymous Gregorian（Meeus/Jones/Butcher），1583 年起通用，已断言 2024/2025/2026/2038

## 已知限制

- 全球部分只收录 28 个「公认且可规则化」的节日；联合国另有约 160 个冷门国际日（世界金枪鱼日、世界驼羊日这类）未收录，需要时在 `data/intl_days.json` 加一行即可
- 母亲节/父亲节采用北美口径（5 月第 2 个周日 / 6 月第 3 个周日），部分国家日期不同
- 中国放假安排来自国务院公告；若某年公告尚未发布，该年只有节日没有休/班标记

## License

[MIT](LICENSE)
