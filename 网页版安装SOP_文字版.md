# 爆款雷达 · 网页版安装 SOP(文字版)

点一个按钮复制模板,全程网页操作。
✋ 零终端 · 不用打任何指令 · 不用装任何软件。

装完之后系统每周自动:抓竞对 IG 爆款 → 转录口播 → AI 拆解 → 改写成你自己语气的口播稿 → 生成可拖拽管理的 dashboard。

---

## 开始前:准备 4 个账号(建议课前先建好)

- GitHub(github.com)— 免费,存代码 + 每周自动运行
- Supabase(supabase.com)— 免费,数据库。注册时选 Continue with GitHub 最快
- Google AI Studio(aistudio.google.com)— 免费,用 Google 账号登录就行。给 AI 拆解 + 我的稿用的 Gemini 钥匙
- Apify(apify.com)— 唯一收费,约 $5/月,负责抓 IG

模板地址(老师会发给你):github.com/alvinokk/viral-radar-template

---

## 第 1 步:复制模板到你的账号(在 GitHub)

1. 打开老师发的模板地址
2. 点右上角绿色按钮「Use this template」→ Create a new repository
3. Repository name 填你想要的名字(例:my-viral-radar)
4. 选 Public → 点 Create repository

比喻:像复制一份 Notion 模板到自己账号——点一下就有。

---

## 第 2 步:建数据库,贴一段 SQL(在 Supabase)

1. supabase.com → New project(Region 选 Singapore,数据库密码自己存好)
2. 左边点 SQL Editor → New query
3. 回到 GitHub 你的仓库,点开 `schema.sql` → 右上角「Copy raw file」(两个小方块的图标),整段复制,贴进 SQL Editor
4. **全篇只改最底下那 5 行**的 `换成竞对1`…`换成竞对5`,换成你要追踪的竞对 IG 账号名(只要账号名,不要 @,不要链接;想多加就复制一行改账号名,建议 8-15 个)。上面一个字都别动
5. 点 Run,看到 Success
6. 左边点 Table Editor,确认 posts 和 competitors 两张表都在,competitors 里是你填的竞对

⚠️ 只改最底下几行,上面一律别动:上面那一大段有安全锁,保证公开钥匙只能读数据、改状态,删不掉你的数据。删了或改了,别人拿到网址就能删光你的东西。

✅ 这段 SQL 可以放心重复跑:不会报错、不会清数据、不会产生重复竞对。贴错了再贴一次、再 Run 一次就好。以后加/停竞对去 Table Editor 改更快。

---

## 第 3 步:复制 3 把钥匙(在 Supabase)

Project Settings → API,复制三样(先放记事本):

- Project URL:https://xxxx.supabase.co
- anon public key:一长串
- service_role key:一长串(私密,下一步只进 Secrets)

⚠️⚠️ 最容易错的一步：Project URL 一定是 https://xxxx.supabase.co 这种。
不要复制你浏览器地址栏那个 supabase.com/dashboard/project/... —— 那是后台页面网址,填错了抓取会直接失败。

---

## 第 4 步:填钥匙和名字(在你的仓库)

你的仓库 → Settings → Secrets and variables → Actions。

先去 Google AI Studio 拿第 5 把钥匙:aistudio.google.com → 用 Google 账号登录 → 左边 Get API key → Create API key → 复制那串 AIza 开头的(免费,不用绑卡)。

① 点 Secrets 分页,New repository secret,加这 5 个(名字一模一样):

| Name | 值 |
|---|---|
| SUPABASE_URL | 第 3 步的 Project URL |
| SUPABASE_ANON_KEY | 第 3 步的 anon key |
| SUPABASE_SERVICE_ROLE_KEY | 第 3 步的 service_role key |
| APIFY_TOKEN | Apify → Settings → API 里的 token |
| GEMINI_API_KEY | 上面 Google AI Studio 拿的那串 |

GEMINI_API_KEY 是 AI 拆解和「我的稿」用的。免费档每天有次数上限,这个系统一周只用一百来次,够用;用完了隔天自动补。
(可选第 6 个:ANTHROPIC_API_KEY —— Claude 的 API key,付费。设了就优先用 Claude,质量更好;没设就用 Gemini。)

② 点 Variables 分页,New repository variable,加这 3 个:

| Name | 值(例) |
|---|---|
| BRAND | 系统名字,例:Yoga Radar |
| NICHE | 你的领域,例:瑜伽教练课程 |
| SYNC_DAY | 每周一 |

⚠️ 注意 SYNC_DAY：值要填「每周一」这种真的星期,别把名字 SYNC_DAY 又填进去,不然网页页脚会显示怪字。

放心贴：贴进网页输入框不会像终端那样贴烂——这是网页版最省心的地方。

---

## 第 5 步:开网页(Pages,在你的仓库)

你的仓库 → Settings → 左边 Pages：

- Source 选 Deploy from a branch
- Branch 选 main,文件夹选 /docs → 点 Save

现在 docs/ 还没生成没关系,先这样设着,跑完第 6 步网页就出来。

---

## 第 6 步:首次运行(在你的仓库)

1. 你的仓库 → Actions 分页,若有提示点「I understand my workflows, enable them」
2. 左边点 Sync Content → 右边 Run workflow → 绿色 Run workflow
3. 之后自动接力:转录 → AI 拆解 → 生成网页。首跑约 10-40 分钟,去忙别的
4. 跑完不用自己拼网址:去 **Settings → Pages**,顶部会显示「Your site is live at …」,点 **Visit site** 就打开你的 dashboard。加书签,以后每周开它。

检查三样:
- [ ] 网页打得开,有爆款卡片
- [ ] 点卡片能播放视频、看口播稿、AI 拆解和绿色的「🎬 我的版本」
- [ ] 拖一张卡到「拍摄中」,出现绿色 ✓(手机也能操作,不用密码)

比喻:电饭煲按下去就走开——网页好了自然在,不用盯着。

---

## 装好之后:每周只做三件事

1. 每周一打开网页,新爆款自动排好队,带口播稿、AI 拆解和「我的稿」
2. 想拍的:点「我的稿」复制 AI 改成你语气的口播稿,直接拍;拖到「拍摄中」,拍完拖「已处理」。团队打开都是同一个看板
3. 加/停竞对:Supabase → Table Editor → competitors 表加行(active 打勾)或取消勾

## 装好之后一定要做一次:告诉 AI 你是谁(我的稿)

「我的稿」是 AI 按你的人设、语气、受众和红线,把每条爆款改写成 30-60 秒可以直接念的中文口播稿。没设之前它用的是一个通用示例人设,稿子不像你。

1. 你的仓库 → 点开 brand_voice.md → 右上角铅笔 ✏️
2. 把每一段的「示例」换成你自己的(人设 / 语气 / 受众痛点 / 敢公开说的承诺 / 红线)。## 开头的标题别动
3. 右上角 Commit changes
4. 重刷已经生成的稿子:Actions → 左边 Rewrite To My Voice → Run workflow → rewrite_all 填 1 → 绿色 Run workflow。跑完再去 Actions → Deploy Dashboard → Run workflow 刷网页

以后新帖自动用新语气,想换语气就重复这 4 步。

---

## 卡住了

| 现象 | 怎么办 |
|---|---|
| 网页 404 | 先等首跑完整结束;再看 Actions 有没有红色失败的 |
| 抓到 0 条 | competitors 表账号拼错 / active 没勾 |
| 标题还是「爆款雷达」 | Variables 的 BRAND 没设,设好后重跑 Deploy Dashboard |
| 有帖子但 AI 拆解是空的 | Secrets 没加 GEMINI_API_KEY(名字一模一样)/ 当天免费额度用完隔天自动补 / 看 Actions → Analyze Posts 日志第一行 [Provider] 和每条的 FAILED: HTTP 几 |
| 卡片没有「我的稿」按钮 | 这条没材料(没口播稿也没像样文案)/ 还没跑到那一步(Actions → Rewrite To My Voice 手动跑)/ 旧 schema 没有 my_script 列(看 Analyze Posts 日志里给的那句 SQL) |

---

## 三条红线

1. service_role key 只进 Secrets,不要贴别处或发群
2. 仓库是 Public,竞对数据和 AI 拆解任何人拿到链接都能看,介意就别用免费版
3. schema.sql 里的安全锁那段不要删

费用:只有 Apify ~$5/月,其余全免费。

有问题把截图发到学员群。
