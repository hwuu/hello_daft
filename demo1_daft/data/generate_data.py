"""
数据生成脚本 - 生成示例产品数据集

用法:
    python generate_data.py --size 100000 --output products.csv
"""

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

# 初始化 Faker
fake = Faker(['zh_CN'])
Faker.seed(42)
random.seed(42)

# 产品类别和子类别
CATEGORIES = {
    '电子产品': ['手机', '电脑', '平板', '耳机', '相机', '智能手表'],
    '家居用品': ['家具', '厨具', '床上用品', '装饰品', '收纳用品'],
    '服装': ['男装', '女装', '童装', '运动装', '鞋类'],
    '图书': ['小说', '技术书籍', '教材', '漫画', '杂志'],
    '食品': ['零食', '饮料', '生鲜', '调味品', '保健品'],
    '运动户外': ['健身器材', '户外装备', '运动服饰', '球类', '自行车'],
    '美妆': ['护肤品', '彩妆', '香水', '个人护理', '美容工具'],
    '玩具': ['益智玩具', '模型', '毛绒玩具', '电子玩具', '拼图']
}

BRANDS = [
    '华为', '小米', '苹果', '三星', '联想', 'OPPO', 'vivo',
    '海尔', '美的', '格力', '索尼', '松下', '飞利浦',
    '耐克', '阿迪达斯', '李宁', '安踏', '特步',
    '无印良品', '宜家', '网易严选', '小米有品'
]

# 产品描述模板（按子类别分组，{brand} 占位符在生成时替换）
DESCRIPTION_TEMPLATES = {
    # === 电子产品 ===
    '手机': [
        '{brand}旗舰手机，搭载最新处理器，6.7英寸AMOLED屏幕，5000mAh大电池，支持67W快充',
        '{brand}轻薄手机，仅重168g，配备5000万像素主摄，续航持久，适合日常使用',
        '{brand}折叠屏手机，创新铰链设计，内屏7.6英寸，外屏6.2英寸，多任务处理更高效',
        '{brand}性价比手机，天玑8000芯片，120Hz高刷屏，5000mAh电池，千元档首选',
        '{brand}影像旗舰手机，1英寸大底主摄，徕卡联合调校，夜景拍摄表现出色',
        '{brand}游戏手机，骁龙8 Gen2处理器，144Hz电竞屏，双X轴线性马达，散热优秀',
    ],
    '电脑': [
        '{brand}轻薄笔记本，14英寸2K屏，酷睿i7处理器，16GB内存，512GB固态硬盘',
        '{brand}游戏本，RTX4060显卡，165Hz电竞屏，32GB内存，散热系统强劲',
        '{brand}商务笔记本，续航12小时，指纹解锁，1.2kg超轻机身，适合移动办公',
        '{brand}台式电脑，i9处理器，RTX4090显卡，64GB内存，专业创作利器',
        '{brand}一体机，27英寸4K屏，简约设计，静音运行，家用办公两相宜',
        '{brand}二合一平板电脑，可拆卸键盘，触控笔支持，轻松切换办公与娱乐模式',
    ],
    '平板': [
        '{brand}平板电脑，11英寸LCD屏，支持手写笔，学习办公娱乐多场景适用',
        '{brand}旗舰平板，12.9英寸Mini-LED屏，M2芯片，专业创作生产力工具',
        '{brand}学生平板，护眼屏幕，内置学习资源，家长管控模式，专为学生设计',
        '{brand}娱乐平板，四扬声器，杜比全景声，追剧观影沉浸体验',
        '{brand}轻薄平板，仅重460g，全金属机身，10小时续航，随身携带无负担',
    ],
    '耳机': [
        '{brand}真无线耳机，主动降噪，30小时总续航，蓝牙5.3，佩戴舒适稳固',
        '{brand}头戴式耳机，Hi-Res认证，40mm大动圈，有线无线双模式',
        '{brand}运动耳机，IP67防水，耳挂式设计，跑步运动不掉落',
        '{brand}降噪耳机，深度降噪40dB，通透模式自然，通话清晰',
        '{brand}游戏耳机，低延迟模式，虚拟7.1声道，RGB灯效，电竞必备',
    ],
    '相机': [
        '{brand}微单相机，2420万像素，4K视频录制，五轴防抖，入门摄影首选',
        '{brand}全画幅相机，6100万像素，15fps连拍，专业级对焦系统',
        '{brand}运动相机，5.3K超高清，防水10米，超强防抖，记录精彩瞬间',
        '{brand}拍立得相机，即拍即得，多种滤镜模式，聚会旅行必备',
        '{brand}数码相机，1英寸传感器，24-200mm变焦，口袋便携旅行利器',
    ],
    '智能手表': [
        '{brand}智能手表，心率血氧监测，GPS定位，14天超长续航，100+运动模式',
        '{brand}运动手表，双频GPS精准定位，气压高度计，专业跑步数据分析',
        '{brand}商务智能手表，蓝宝石表镜，钛合金表壳，NFC支付，经典外观',
        '{brand}健康手表，ECG心电图，血压监测，睡眠分析，健康管理助手',
        '{brand}儿童手表，4G通话，实时定位，SOS求助，家长远程管控',
    ],
    # === 家居用品 ===
    '家具': [
        '{brand}实木餐桌，北欧简约风格，白橡木材质，可容纳6人用餐',
        '{brand}人体工学椅，4D扶手，腰部支撑可调，久坐不累，办公必备',
        '{brand}布艺沙发，高密度海绵填充，可拆洗沙发套，客厅百搭款',
        '{brand}智能升降桌，电动调节高度，记忆三档位，站坐交替更健康',
        '{brand}实木书架，五层开放式设计，承重力强，书房收纳好帮手',
    ],
    '厨具': [
        '{brand}不粘锅，麦饭石涂层，少油烹饪，电磁炉燃气灶通用',
        '{brand}刀具套装，德国钢材，锋利持久，含菜刀、水果刀、剪刀等7件',
        '{brand}电饭煲，IH电磁加热，智能预约，3L容量，米饭粒粒分明',
        '{brand}破壁机，1200W大功率，8叶刀头，豆浆果汁辅食一机多用',
        '{brand}空气炸锅，无油健康烹饪，5.5L大容量，触控面板，操作简便',
    ],
    '床上用品': [
        '{brand}四件套，全棉60支长绒棉，亲肤透气，简约纯色设计',
        '{brand}乳胶枕，泰国天然乳胶，人体工学曲线，缓解颈椎压力',
        '{brand}蚕丝被，100%桑蚕丝填充，轻盈保暖，四季通用',
        '{brand}记忆棉床垫，慢回弹材质，贴合身体曲线，独立弹簧静音',
        '{brand}凉席，冰丝材质，可折叠水洗，夏季清凉透气',
    ],
    '装饰品': [
        '{brand}北欧风挂画，简约抽象艺术，铝合金画框，客厅卧室装饰',
        '{brand}香薰蜡烛，天然大豆蜡，持久留香8小时，助眠放松',
        '{brand}绿植花瓶，陶瓷材质，哑光釉面，桌面摆件增添生机',
        '{brand}LED氛围灯，遥控调光调色，USB供电，营造温馨氛围',
        '{brand}墙面置物架，免打孔安装，实木隔板，装饰收纳两不误',
    ],
    '收纳用品': [
        '{brand}衣物收纳箱，PP材质，可视窗口设计，防尘防潮，换季收纳必备',
        '{brand}桌面收纳盒，多格分区，化妆品文具整理，保持桌面整洁',
        '{brand}鞋柜收纳架，免安装折叠，透明可视，节省空间',
        '{brand}厨房置物架，不锈钢材质，多层设计，调料瓶碗碟分类存放',
        '{brand}真空压缩袋，加厚材质，手动抽气，被子衣物缩小体积',
    ],
    # === 服装 ===
    '男装': [
        '{brand}纯棉T恤，圆领短袖，透气吸汗，基础百搭款，多色可选',
        '{brand}商务衬衫，免烫面料，修身剪裁，职场通勤必备',
        '{brand}休闲夹克，防风防泼水，立领设计，春秋薄款外套',
        '{brand}牛仔裤，弹力面料，直筒版型，经典水洗工艺',
        '{brand}羽绒服，800蓬白鹅绒，轻量保暖，可收纳便携',
    ],
    '女装': [
        '{brand}连衣裙，雪纺面料，碎花印花，收腰显瘦，夏季清新款',
        '{brand}针织开衫，柔软亲肤，宽松慵懒风，春秋内搭外穿皆宜',
        '{brand}西装外套，垂感面料，一粒扣设计，通勤休闲两穿',
        '{brand}高腰阔腿裤，冰丝面料，垂坠感好，显瘦显高',
        '{brand}羊绒大衣，双面呢工艺，经典翻领，秋冬优雅之选',
    ],
    '童装': [
        '{brand}儿童卫衣，纯棉面料，卡通印花，柔软亲肤，不起球',
        '{brand}儿童羽绒服，90%白鸭绒，防风保暖，活泼配色',
        '{brand}儿童运动套装，速干面料，弹力舒适，适合户外活动',
        '{brand}婴儿连体衣，A类标准，无骨缝制，新生儿贴身穿着',
        '{brand}儿童防晒衣，UPF50+，轻薄透气，夏季户外防护',
    ],
    '运动装': [
        '{brand}速干运动T恤，吸湿排汗面料，跑步健身训练适用',
        '{brand}瑜伽裤，高腰提臀，四面弹力，裸感面料，运动日常两穿',
        '{brand}运动套装，连帽卫衣+束脚裤，休闲运动风，舒适百搭',
        '{brand}压缩衣，梯度压缩技术，减少肌肉疲劳，专业运动装备',
        '{brand}防风跑步外套，轻量防泼水，反光条设计，夜跑更安全',
    ],
    '鞋类': [
        '{brand}跑步鞋，缓震回弹中底，透气网面，轻量化设计',
        '{brand}休闲板鞋，头层牛皮，经典小白鞋款式，百搭舒适',
        '{brand}登山鞋，防水透气，Vibram大底，抓地力强，户外徒步首选',
        '{brand}凉鞋，软木鞋床，可调节搭扣，夏季舒适出行',
        '{brand}商务皮鞋，头层牛皮，橡胶底防滑，正装场合必备',
    ],
    # === 图书 ===
    '小说': [
        '畅销悬疑小说，跌宕起伏的剧情，烧脑推理让人欲罢不能',
        '经典文学名著，影响几代人的作品，精装典藏版，值得反复阅读',
        '都市情感小说，细腻笔触描绘现代人的爱情与生活',
        '科幻长篇小说，宏大的宇宙观设定，硬核科幻爱好者必读',
        '历史小说，以真实历史为背景，再现波澜壮阔的时代画卷',
    ],
    '技术书籍': [
        'Python编程从入门到实践，案例驱动教学，适合零基础学习者',
        '深入理解计算机系统，经典教材，程序员进阶必读',
        '机器学习实战，理论与代码结合，含大量实战项目',
        '数据库系统概论，全面讲解关系型与NoSQL数据库原理',
        '云原生架构设计，微服务、容器化、DevOps最佳实践',
    ],
    '教材': [
        '高等数学教材，例题丰富，解题思路清晰，考研复习推荐',
        '大学英语综合教程，听说读写全面训练，配套在线资源',
        '经济学原理，通俗易懂的经济学入门教材，案例贴近生活',
        '有机化学教材，系统讲解反应机理，实验指导详尽',
        '线性代数教材，矩阵理论与应用，配套习题解答',
    ],
    '漫画': [
        '日系热血漫画，精彩的战斗场面，燃爆的剧情发展',
        '治愈系漫画，温暖的日常故事，阅读后心情愉悦',
        '国漫精品，水墨画风，融合中国传统文化元素',
        '悬疑推理漫画，环环相扣的谜题，结局出人意料',
        '科幻漫画，未来世界观设定，画面精美细腻',
    ],
    '杂志': [
        '科技前沿杂志，报道最新科技动态，深度分析行业趋势',
        '时尚生活杂志，潮流穿搭指南，生活美学分享',
        '国家地理杂志，震撼自然摄影，探索世界奇观',
        '商业财经杂志，企业案例分析，投资理财知识',
        '文学期刊，收录优秀原创作品，文学爱好者的精神食粮',
    ],
    # === 食品 ===
    '零食': [
        '{brand}坚果礼盒，每日坚果混合装，科学配比，健康美味',
        '{brand}肉脯干，精选猪后腿肉，炭火烘烤，香辣口味，追剧零食',
        '{brand}曲奇饼干，进口黄油，手工烘焙，酥脆可口，下午茶首选',
        '{brand}果干蜜饯，天然水果制作，无添加防腐剂，酸甜开胃',
        '{brand}薯片，非油炸工艺，多种口味可选，轻薄脆爽',
    ],
    '饮料': [
        '{brand}矿泉水，天然水源地，富含矿物质，550ml便携装',
        '{brand}气泡水，0糖0卡，多种果味，清爽解渴',
        '{brand}鲜榨果汁，NFC非浓缩还原，冷藏保鲜，营养丰富',
        '{brand}咖啡液，冷萃工艺，即溶速饮，浓郁醇香',
        '{brand}茶饮料，原叶萃取，低糖配方，回甘持久',
    ],
    '生鲜': [
        '{brand}有机蔬菜礼盒，当日采摘，冷链配送，新鲜直达',
        '{brand}进口牛排，澳洲安格斯M5级，原切雪花牛排，口感嫩滑',
        '{brand}海鲜礼盒，鲜活大闸蟹，产地直发，膏满黄肥',
        '{brand}水果礼盒，精选当季水果，果形饱满，甜度高',
        '{brand}鲜牛奶，牧场直供，巴氏杀菌，营养新鲜，每日配送',
    ],
    '调味品': [
        '{brand}酱油，古法酿造180天，鲜味浓郁，炒菜提鲜必备',
        '{brand}橄榄油，西班牙进口，特级初榨，凉拌烹饪皆宜',
        '{brand}花椒粉，四川汉源大红袍花椒，麻香浓郁，川菜必备',
        '{brand}蚝油，鲜蚝熬制，鲜味十足，炒菜拌面增香提味',
        '{brand}黑胡椒，研磨瓶装，现磨现用，牛排西餐调味',
    ],
    '保健品': [
        '{brand}维生素C片，天然VC提取，增强免疫力，每日一片',
        '{brand}鱼油软胶囊，深海鱼油，富含Omega-3，呵护心脑血管',
        '{brand}益生菌粉，300亿活菌，调节肠道菌群，改善消化',
        '{brand}钙片，碳酸钙+维生素D3，促进钙吸收，中老年补钙',
        '{brand}蛋白粉，乳清蛋白，健身增肌，运动后快速补充',
    ],
    # === 运动户外 ===
    '健身器材': [
        '{brand}可调节哑铃，2-20kg自由切换，家庭健身必备',
        '{brand}跑步机，折叠静音设计，15档坡度调节，家用商用两宜',
        '{brand}瑜伽垫，TPE双面防滑，6mm加厚，回弹性好，附带收纳带',
        '{brand}弹力带套装，5级阻力，全身训练，便携易收纳',
        '{brand}划船机，水阻设计，模拟真实划船体验，全身有氧训练',
    ],
    '户外装备': [
        '{brand}登山包，50L大容量，背负系统透气，防雨罩配备',
        '{brand}帐篷，双层防暴雨，3-4人空间，铝合金杆轻量化',
        '{brand}睡袋，鹅绒填充，舒适温度-10℃，压缩体积小',
        '{brand}户外冲锋衣，三合一设计，防风防水透气，四季可穿',
        '{brand}登山杖，碳纤维材质，三节折叠，减震手柄，轻便耐用',
    ],
    '运动服饰': [
        '{brand}运动短裤，速干面料，内置衬裤，跑步训练适用',
        '{brand}运动内衣，中强度支撑，透气排汗，健身瑜伽必备',
        '{brand}运动袜，加厚毛圈底，吸汗防臭，跑步篮球通用',
        '{brand}运动头带，弹力吸汗，防滑设计，运动时固定发型',
        '{brand}防晒袖套，UPF50+，冰丝凉感，户外运动防晒',
    ],
    '球类': [
        '{brand}篮球，PU材质，室内外通用，手感好弹性佳',
        '{brand}足球，FIFA认证，热贴合工艺，比赛训练用球',
        '{brand}羽毛球拍，碳纤维材质，攻守兼备，含拍包和手胶',
        '{brand}乒乓球拍，双面反胶，弧圈快攻型，送3个训练球',
        '{brand}网球，ITF认证比赛用球，耐打弹性好，3只罐装',
    ],
    '自行车': [
        '{brand}山地自行车，27速变速，铝合金车架，前叉避震，越野骑行',
        '{brand}公路自行车，碳纤维车架，Shimano变速套件，竞速利器',
        '{brand}折叠自行车，20英寸，3秒快折，地铁公交可携带',
        '{brand}电助力自行车，锂电池续航60km，助力骑行省力通勤',
        '{brand}儿童自行车，辅助轮可拆卸，安全刹车，适合4-8岁',
    ],
    # === 美妆 ===
    '护肤品': [
        '{brand}保湿面霜，玻尿酸成分，深层补水锁水，干皮救星',
        '{brand}防晒霜，SPF50+ PA++++，轻薄不油腻，日常通勤防晒',
        '{brand}精华液，烟酰胺美白精华，淡化暗沉，提亮肤色',
        '{brand}洁面乳，氨基酸配方，温和清洁，敏感肌适用',
        '{brand}面膜，蚕丝膜布，精华液充足，急救补水，一盒10片',
    ],
    '彩妆': [
        '{brand}口红，丝绒雾面质地，显色持久，不易脱色',
        '{brand}粉底液，持妆12小时，自然遮瑕，多色号可选',
        '{brand}眼影盘，12色大地色系，哑光珠光搭配，日常百搭',
        '{brand}睫毛膏，纤长卷翘，防水防汗，不晕染不结块',
        '{brand}腮红，细腻粉质，自然好气色，配刷头方便携带',
    ],
    '香水': [
        '{brand}淡香水，花果调，前调柑橘清新，中调玫瑰优雅，留香6小时',
        '{brand}男士香水，木质调，沉稳大气，商务社交场合适用',
        '{brand}中性香水，海洋调，清新自然，男女皆宜，日常通勤',
        '{brand}浓香水，东方调，琥珀与香草，浓郁持久，秋冬适用',
        '{brand}香水礼盒，经典香型迷你装，5ml×4支，送礼自用皆宜',
    ],
    '个人护理': [
        '{brand}电动牙刷，声波震动，5种清洁模式，续航30天',
        '{brand}洗发水，无硅油配方，控油蓬松，改善头皮出油',
        '{brand}沐浴露，烟酰胺美白，持久留香，滋润不假滑',
        '{brand}剃须刀，5刀头浮动贴面，干湿双剃，全身水洗',
        '{brand}身体乳，烟酰胺+果酸，美白去鸡皮，滋润保湿',
    ],
    '美容工具': [
        '{brand}化妆刷套装，动物毛+纤维毛，12支装，含收纳包',
        '{brand}美容仪，射频提拉紧致，EMS微电流，居家美容院级护理',
        '{brand}卷发棒，陶瓷涂层，32mm卷径，快速升温，不伤发质',
        '{brand}洁面仪，硅胶刷头，声波震动，深层清洁毛孔',
        '{brand}美甲灯，UV+LED双光源，快速固化，美甲DIY必备',
    ],
    # === 玩具 ===
    '益智玩具': [
        '{brand}磁力片积木，100片装，多种造型拼搭，锻炼空间想象力',
        '{brand}编程机器人，图形化编程，寓教于乐，培养逻辑思维',
        '{brand}数独游戏棋，多难度关卡，亲子互动，锻炼数学思维',
        '{brand}科学实验套装，50+实验项目，安全材料，激发科学兴趣',
        '{brand}七巧板，榉木材质，经典益智玩具，幼儿启蒙教育',
    ],
    '模型': [
        '{brand}高达拼装模型，1/144比例，精密零件，还原度高',
        '{brand}合金汽车模型，1:18比例，可开门引擎盖，收藏级品质',
        '{brand}积木城市系列，1000+颗粒，还原经典建筑，拼装乐趣',
        '{brand}航模飞机，遥控电动，6通道操控，户外飞行体验',
        '{brand}军事模型，1/35比例坦克，细节精致，军事爱好者收藏',
    ],
    '毛绒玩具': [
        '{brand}泰迪熊公仔，60cm大号，PP棉填充，柔软可抱，送礼佳品',
        '{brand}卡通玩偶，正版授权，做工精细，儿童陪伴好伙伴',
        '{brand}安抚玩偶，婴儿级面料，可水洗，新生儿安抚入睡',
        '{brand}恐龙毛绒玩具，仿真造型，多种恐龙可选，男孩最爱',
        '{brand}猫咪抱枕，记忆棉填充，午睡靠垫两用，办公室必备',
    ],
    '电子玩具': [
        '{brand}遥控汽车，2.4G遥控，四驱越野，可充电，时速20km/h',
        '{brand}儿童平衡车，无脚踏设计，锻炼平衡能力，适合2-6岁',
        '{brand}泡泡机，电动全自动，一键出泡，户外派对神器',
        '{brand}儿童相机，2000万像素，硅胶防摔壳，培养摄影兴趣',
        '{brand}电子琴，61键力度感应，内置教学模式，儿童音乐启蒙',
    ],
    '拼图': [
        '{brand}1000片风景拼图，高清印刷，厚实纸板，减压休闲',
        '{brand}3D立体拼图，世界名建筑系列，拼装后可做摆件',
        '{brand}儿童拼图，大块设计，圆角安全，认知启蒙，适合3岁+',
        '{brand}木质拼图，异形拼块，动物造型，成人解压玩具',
        '{brand}磁性拼图书，便携设计，旅途打发时间，多主题可选',
    ],
}


def generate_product_data(size: int = 100000) -> pd.DataFrame:
    """
    生成产品数据集

    Args:
        size: 生成的记录数量

    Returns:
        pandas DataFrame
    """
    print(f"正在生成 {size:,} 条产品记录...")

    data = []
    start_date = datetime.now() - timedelta(days=365)

    for i in range(size):
        if (i + 1) % 10000 == 0:
            print(f"已生成 {i + 1:,} 条记录...")

        # 选择类别和子类别
        category = random.choice(list(CATEGORIES.keys()))
        subcategory = random.choice(CATEGORIES[category])

        # 生成价格
        original_price = round(random.uniform(10, 5000), 2)
        discount = random.choice([0, 5, 10, 15, 20, 25, 30, 40, 50])
        price = round(original_price * (1 - discount / 100), 2)

        # 生成评分和评论数
        rating = round(random.uniform(3.0, 5.0), 1)
        review_count = random.randint(0, 10000)

        # 生成库存
        stock = random.randint(0, 1000)

        # 生成时间戳
        created_at = start_date + timedelta(
            days=random.randint(0, 365),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        updated_at = created_at + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23)
        )

        # 随机引入缺失值（约3%品牌为空）
        if random.random() < 0.03:
            brand = None
        else:
            brand = random.choice(BRANDS)

        # 随机引入缺失值（约5%描述为空）
        if random.random() < 0.05:
            description = None
        else:
            template = random.choice(DESCRIPTION_TEMPLATES[subcategory])
            description = template.format(brand=brand or '未知品牌')

        # 创建记录
        record = {
            'product_id': f'P{i+1:08d}',
            'name': f'{brand or "未知品牌"} {subcategory} {fake.word()}',
            'category': category,
            'subcategory': subcategory,
            'price': price,
            'original_price': original_price,
            'discount': discount,
            'rating': rating if random.random() > 0.02 else None,
            'review_count': review_count,
            'stock': stock,
            'brand': brand,
            'description': description,
            'created_at': created_at,
            'updated_at': updated_at
        }

        data.append(record)

    # 创建 DataFrame
    df = pd.DataFrame(data)

    # 引入一些重复记录（约2%）
    duplicate_count = int(size * 0.02)
    if duplicate_count > 0:
        duplicates = df.sample(n=duplicate_count, random_state=42)
        df = pd.concat([df, duplicates], ignore_index=True)
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    print(f"✓ 成功生成 {len(df):,} 条记录（包含 {duplicate_count:,} 条重复记录）")

    return df


def save_data(df: pd.DataFrame, output_dir: str = '.'):
    """
    保存数据为多种格式

    Args:
        df: pandas DataFrame
        output_dir: 输出目录
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("\n正在保存数据...")

    # CSV
    csv_path = output_path / 'products.csv'
    df.to_csv(csv_path, index=False)
    csv_size = csv_path.stat().st_size / (1024 * 1024)
    print(f"✓ CSV: {csv_path} ({csv_size:.2f} MB)")

    # Parquet
    parquet_path = output_path / 'products.parquet'
    df.to_parquet(parquet_path, index=False, engine='pyarrow')
    parquet_size = parquet_path.stat().st_size / (1024 * 1024)
    print(f"✓ Parquet: {parquet_path} ({parquet_size:.2f} MB)")

    # JSON
    json_path = output_path / 'products.json'
    df.to_json(json_path, orient='records', lines=True)
    json_size = json_path.stat().st_size / (1024 * 1024)
    print(f"✓ JSON: {json_path} ({json_size:.2f} MB)")

    print(f"\n数据统计:")
    print(f"  总记录数: {len(df):,}")
    print(f"  列数: {len(df.columns)}")
    print(f"  缺失值: {df.isnull().sum().sum():,}")
    print(f"  重复记录: {df.duplicated().sum():,}")
    print(f"\n类别分布:")
    print(df['category'].value_counts())


def main():
    parser = argparse.ArgumentParser(description='生成示例产品数据集')
    parser.add_argument(
        '--size',
        type=int,
        default=100000,
        help='生成的记录数量（默认: 100000）'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='.',
        help='输出目录（默认: 当前目录）'
    )

    args = parser.parse_args()

    # 生成数据
    df = generate_product_data(args.size)

    # 保存数据
    save_data(df, args.output)

    print("\n✓ 数据生成完成！")
    print("\n使用方法:")
    print("  import daft")
    print("  df = daft.read_csv('products.csv')")
    print("  # 或使用 Parquet 格式（推荐）")
    print("  df = daft.read_parquet('products.parquet')")


if __name__ == '__main__':
    main()
