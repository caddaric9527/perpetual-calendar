# 📅 万年历 · 中美节日日历订阅

一条 iCalendar 订阅链接，把**中国农历节日 + 二十四节气 + 美国法定假日**同步到 Apple 日历 / Outlook / Google 日历。订阅一次，往后每年自动更新，不用再手动导入。

![iCal](https://img.shields.io/badge/iCalendar-RFC%205545-success)
![Apple](https://img.shields.io/badge/Apple%20Calendar-订阅支持-black)
![years](https://img.shields.io/badge/覆盖-2020–2060-blue)
![license](https://img.shields.io/badge/license-MIT-green)

## 订阅地址

| 日历 | 内容 | 订阅 |
| --- | --- | --- |
| 全部 | 中国节日 + 节气 + 美国节日，共约 2800 条 | `webcal://caddaric9527.github.io/perpetual-calendar/all.ics` |
| 中国 | 农历传统节日、公历纪念日、24 节气 | `webcal://caddaric9527.github.io/perpetual-calendar/cn.ics` |
| 美国 | 11 个联邦法定假日（含补休）+ 常见民间节日 | `webcal://caddaric9527.github.io/perpetual-calendar/us.ics` |

> 网页版一键订阅：<https://caddaric9527.github.io/perpetual-calendar/>
> 若客户端只认 `https://`，把 `webcal://` 换成 `https://` 即可。

**iPhone / iPad**：点订阅链接 → 「订阅」→ 完成；或 设置 → 日历 → 账户 → 添加账户 → 其他 → 添加已订阅的日历。
**Mac**：日历 App → 文件 → 新建日历订阅 → 粘贴链接 → 刷新频率选「每天」。

## 包含内容

**🇨🇳 中国**
- 农历节日：春节、元宵、龙抬头、端午、七夕、中元、中秋、重阳、腊八、小年、除夕（含农历日期与干支生肖年）
- 公历纪念日：元旦、情人节、妇女节、植树节、劳动节、青年节、儿童节、建党节、建军节、教师节、国庆节
- 二十四节气：全年 24 个节气精确到日（清明同时作为节日条目）

**🇺🇸 美国**
- 联邦法定假日 11 个，固定日期节日自动生成 **补休日**（周六→周五、周日→周一）：元旦、马丁·路德·金日、总统日、阵亡将士纪念日、六月节、独立日、劳动节、哥伦布日、退伍军人节、感恩节、圣诞节
- 民间节日：情人节、圣帕特里克节、愚人节、地球日、复活节（含耶稣受难日）、母亲节、父亲节、万圣节、土拨鼠日、选举日（偶数年）
- 夏令时开始 / 结束提醒

## 本地使用

```bash
pip install -r requirements.txt

python selftest.py                        # 校验关键节日日期
python generate.py                        # 生成到 docs/（默认 2020-2060）
python generate.py --from-year 1900 --to-year 2099   # 农历数据全范围
python generate.py --out public --site https://example.github.io/x
```

参数说明：

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `--from-year` / `--to-year` | 2020 / 2060 | 支持 1900–2099（受农历数据表限制） |
| `--out` | `docs` | 输出目录 |
| `--site` | 本仓库 Pages 地址 | 写入 `SOURCE` 属性 |
| `--overrides` | `data/holidays_cn.json` | 法定节假日/调休数据 |
| `--no-terms` | 关闭 | 不包含二十四节气 |

## 维护官方放假安排（可选）

国务院每年公布次年放假安排，属于**行政公告而非可推算规则**，因此不内置。想看到「🏖️ 休 / 💼 班」标记，编辑 `data/holidays_cn.json`：

```json
{
  "2026-02-17": { "type": "休", "name": "春节假期" },
  "2026-02-14": { "type": "班", "name": "春节调休上班" }
}
```

推送后 CI 自动重建。

## 工作流

`.github/workflows/build.yml`：

1. 安装依赖 → 运行 `selftest.py`（日期断言不通过则构建失败）
2. `generate.py` 生成三个 `.ics` 到 `docs/`
3. 变更回写仓库（`[skip ci]` 防循环）
4. `actions/configure-pages`（`enablement: true`）→ 上传 → 部署 GitHub Pages
5. 每周一自动重跑，保持 `DTSTAMP` / 刷新时间新鲜

## 项目结构

```
calgen/
  ical.py     RFC 5545 生成器（UTF-8 折行 75 字节、全天事件、稳定 UID）
  china.py    农历节日、公历纪念日、二十四节气
  usa.py      联邦假日、补休规则、复活节 computus、夏令时
generate.py   CLI：生成 all.ics / cn.ics / us.ics
selftest.py   关键日期自检（2033 闰月问题年等已覆盖）
data/         法定节假日/调休数据
docs/         落地页 + 生成的 .ics（Pages 根目录）
```

## 技术要点

- **稳定 UID**：`{YYYYMMDD}-{slug}@perpetual-calendar`，重新生成不会在客户端产生重复事件
- **全天事件**：`DTSTART;VALUE=DATE` + 次日 `DTEND`，不占用时段（`TRANSP:TRANSPARENT`）
- **自动刷新**：`REFRESH-INTERVAL` / `X-PUBLISHED-TTL: P1D`，Apple 日历每日拉取
- **UTF-8 折行**：按字节切分且不切断多字节字符，中文字段在老客户端也不乱码

## 数据准确性

- 农历、干支、节气来自 [cnlunar](https://github.com/OPN48/cnlunar) 与 [zhdate](https://github.com/CutePandaSh/zhdate)，覆盖 1900–2099（含 2033 闰十一月问题年）
- 美国联邦假日按 5 U.S.C. 规则推算，复活节用 Anonymous Gregorian algorithm
- 中国**法定放假安排（含调休）**需人工录入，见上文

## License

[MIT](LICENSE)
