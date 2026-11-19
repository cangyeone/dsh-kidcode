// 编程小课堂
//  1) 首页课程面板：编程 + 地震科普 两条线，只在 kidcode 预设的会话里出现。
//  2) 会话头部「课程」按钮。
//
// 点卡片 = 把该课的请求写进输入框（不另开会话），孩子按发送开始。
window.__ModuleLoader__.load({
  id: '@cangyeone/dsh-kidcode',
  factory(require) {
    const React = require('react');
    const h = React.createElement;

    const KIDCODE = 'kidcode';

    const tracks = [
      {
        id: 'code',
        name: '编程',
        hint: '让屏幕听话：点 → 线 → 图形 → 作品',
        color: '#4f8cff',
        lessons: [
          ['01', '坐标', '点亮一个像素', '#4f8cff'],
          ['02', '循环', '画一条线', '#5aa9ff'],
          ['03', '函数', '画一张格子纸', '#48c2d8'],
          ['04', '五角星', '画个五角星', '#ffb020'],
          ['05', '条件', '按一下换图形', '#ff8a3d'],
          ['06', '变量', '记下按了几次', '#ff6b6b'],
          ['07', '数据', '把震动画出来', '#c86bff'],
          ['08', '阈值', '让 AI 更敏感', '#8f6bff'],
          ['09', '误差', '为什么数不一样', '#6b8bff'],
          ['10', '随机', '撒一把沙子', '#2fbf9b'],
          ['11', '分类', '机器怎么认', '#43c96a'],
          ['12', '综合', '画一幅作品', '#e0a030'],
        ],
      },
      {
        id: 'quake',
        name: '地震科普',
        hint: '震动 → 地震 → 检测，每课都上真机',
        color: '#ff8a3d',
        lessons: [
          ['01', '敲桌子', '振动是什么', '#ff8a3d'],
          ['02', '有多大力', '振幅与量程', '#ff6b6b'],
          ['03', '有多快', '频率与滤波', '#c86bff'],
          ['04', 'P 波和 S 波', '为什么先到的不是最狠的', '#8f6bff'],
          ['05', '震中在哪', '单台站能算多远', '#4f8cff'],
          ['06', '地震多大', '震级不是振幅', '#5aa9ff'],
          ['07', '凭什么说这是地震', '阈值、误报、漏报', '#2fbf9b'],
          ['08', 'AI 怎么听', '模型、概率、预热', '#43c96a'],
        ],
      },
    ];

    const styles = `
      .kc-panel { width:100%; max-width:780px; margin:0 auto; padding:8px 4px 4px; }
      .kc-head { display:flex; align-items:center; gap:10px; margin-bottom:12px; }
      .kc-star { font-size:20px; color:#ffb020; animation: kc-spin 9s linear infinite; }
      @keyframes kc-spin { to { transform: rotate(360deg); } }
      .kc-title { font-size:17px; font-weight:600; letter-spacing:.6px; }
      .kc-sub { font-size:12px; opacity:.55; margin-left:auto; }
      .kc-track { margin-top:14px; }
      .kc-track-head { display:flex; align-items:baseline; gap:8px; margin-bottom:8px; }
      .kc-track-name { font-size:13px; font-weight:600; color:var(--kc-track); }
      .kc-track-hint { font-size:11px; opacity:.55; }
      .kc-grid { display:grid; gap:9px; grid-template-columns:repeat(auto-fill, minmax(170px, 1fr)); }
      .kc-card {
        position:relative; text-align:left; font:inherit; cursor:pointer;
        display:flex; flex-direction:column; gap:4px;
        padding:12px 13px 13px; border-radius:13px;
        background:linear-gradient(155deg, var(--kc-bg), transparent 72%);
        border:1px solid var(--kc-line);
        transition: transform .13s ease, box-shadow .13s ease;
        overflow:hidden;
      }
      .kc-card::after { content:''; position:absolute; inset:0 auto 0 0; width:4px; background:var(--kc-ink); opacity:.9; }
      .kc-card:hover { transform:translateY(-2px); box-shadow:0 8px 22px rgba(0,0,0,.18); }
      .kc-card:active { transform:translateY(0); }
      .kc-card:focus-visible { outline:2px solid var(--kc-ink); outline-offset:2px; }
      .kc-no { font-size:11px; font-weight:700; letter-spacing:1.5px; color:var(--kc-ink); }
      .kc-name { font-size:14px; font-weight:600; }
      .kc-goal { font-size:11px; opacity:.6; }
      .kc-foot { margin-top:14px; font-size:11px; opacity:.5; }
      .kc-outline {
        width:100%; height:100%; overflow:auto;
        padding:20px 24px 140px; box-sizing:border-box;
      }
      .kc-outline .kc-panel { max-width:none; }
      .kc-outline .kc-grid { grid-template-columns:repeat(auto-fill, minmax(150px, 1fr)); }
      .kc-tab {
        font:inherit; font-size:12px; cursor:pointer; display:inline-flex;
        align-items:center; gap:5px; padding:3px 9px; border-radius:8px;
        border:1px solid rgba(127,127,127,.28); background:transparent; color:inherit;
      }
      .kc-tab:hover { background:rgba(127,127,127,.12); }
      .kc-tab:focus-visible { outline:2px solid #ffb020; outline-offset:2px; }
      .kc-struct {
        margin-top:16px; display:flex; gap:16px; align-items:center;
        padding:12px 14px; border-radius:14px;
        background:linear-gradient(120deg, rgba(79,140,255,.10), rgba(255,176,32,.10));
        border:1px solid rgba(127,127,127,.18);
      }
      .kc-struct svg { flex:0 0 auto; width:256px; height:64px; }
      .kc-struct-line {
        fill:none; stroke:#ffb020; stroke-width:1.5; stroke-linejoin:round; stroke-linecap:round;
        stroke-dasharray:220; stroke-dashoffset:220;
        animation: kc-draw 4.2s ease-in-out infinite;
      }
      .kc-struct-dot { fill:#4f8cff; animation: kc-pop 4.2s ease-in-out infinite; }
      @keyframes kc-draw { 0% { stroke-dashoffset:220; } 55% { stroke-dashoffset:0; } 100% { stroke-dashoffset:0; } }
      @keyframes kc-pop { 0%,8% { opacity:0; transform:scale(.4); } 20% { opacity:1; transform:scale(1); } 100% { opacity:1; } }
      .kc-struct-text { font-size:12px; line-height:1.75; }
      .kc-struct-text b { font-size:12px; }
      .kc-struct-text span { opacity:.6; }
      @media (prefers-reduced-motion: reduce) {
        .kc-star, .kc-struct-line, .kc-struct-dot { animation:none; }
        .kc-struct-line { stroke-dashoffset:0; }
        .kc-card, .kc-tab { transition:none; }
      }
    `;

    // 槽位把 sessionId 和 useSessions 传给组件；用它实时读会话预设。
    function usePresetId(props) {
      const useSessions = typeof props.useSessions === 'function' ? props.useSessions : () => undefined;
      return useSessions((state) => {
        const sessionId = props.sessionId;
        if (sessionId === undefined || state === undefined) return undefined;
        const entry = state.byId && state.byId[sessionId];
        const value = entry && entry.projectionValues && entry.projectionValues.agentPreset;
        return typeof value === 'string' ? value : undefined;
      });
    }

    function makeOpener(ctx, inputActions) {
      return (track, number, name) => {
        if (number === null) {
          // 头部「课程」按钮：开一节新的空白课，回到首页课程表。
          try {
            ctx.uiWorkspace.startSession(undefined, { agentPreset: KIDCODE });
          } catch (error) {
            console.warn('[kidcode-courses] 打开课程表失败', error);
          }
          return;
        }
        const label = track === 'quake' ? '地震科普' : '编程';
        const prompt = label + '第 ' + number + ' 课：' + name + '。先带我做第一个确认。';
        try {
          if (inputActions && typeof inputActions.setDraft === 'function') {
            inputActions.setDraft(prompt);
            return;
          }
          ctx.uiWorkspace.startSession(undefined, { agentPreset: KIDCODE, prompt });
        } catch (error) {
          console.warn('[kidcode-courses] 打开课程失败', error);
        }
      };
    }

    const STAR_POINTS = '128,11 140,49 108,26 148,26 116,49 128,11';
    const STAR_DOTS = [[128, 11], [140, 49], [108, 26], [148, 26], [116, 49]];

    function Structure() {
      return h(
        'div',
        { className: 'kc-struct' },
        h(
          'svg',
          { viewBox: '0 0 256 64', role: 'img', 'aria-label': '五角星的绘制过程' },
          h('polyline', { className: 'kc-struct-line', points: STAR_POINTS }),
          ...STAR_DOTS.map(([x, y], index) =>
            h('circle', {
              key: 'd' + index,
              className: 'kc-struct-dot',
              cx: x,
              cy: y,
              r: 2.2,
              style: { animationDelay: index * 0.12 + 's' },
            }),
          ),
        ),
        h(
          'div',
          { className: 'kc-struct-text' },
          h('div', null, h('b', null, '顶点'), ' 5 个', h('span', null, ' — 先定位置')),
          h('div', null, h('b', null, '线段'), ' 5 条', h('span', null, ' — 再定连法（隔一个连）')),
          h('div', null, h('b', null, '画布'), ' 256 × 64', h('span', null, ' = 2048 字节')),
          h('div', null, h('span', null, '点一个顶点，屏幕就亮一个格子；线是点排出来的。')),
        ),
      );
    }

    function Track({ track, open }) {
      return h(
        'div',
        { className: 'kc-track', style: { '--kc-track': track.color } },
        h(
          'div',
          { className: 'kc-track-head' },
          h('span', { className: 'kc-track-name' }, track.name),
          h('span', { className: 'kc-track-hint' }, track.hint),
        ),
        h(
          'div',
          { className: 'kc-grid' },
          ...track.lessons.map(([number, name, goal, hue]) =>
            h(
              'button',
              {
                key: track.id + number,
                type: 'button',
                className: 'kc-card',
                title: number + ' ' + name + '：' + goal,
                style: { '--kc-ink': hue, '--kc-bg': hue + '26', '--kc-line': hue + '55' },
                onClick: () => open(track.id, number, name),
              },
              h('span', { className: 'kc-no' }, number),
              h('span', { className: 'kc-name' }, name),
              h('span', { className: 'kc-goal' }, goal),
            ),
          ),
        ),
      );
    }

    function Panel(props) {
      const preset = usePresetId(props);
      const open = props.openLesson;
      if (preset !== KIDCODE) return null;
      return h(
        'div',
        { className: 'kc-panel' },
        h('style', { key: 'style' }, styles),
        h(
          'div',
          { className: 'kc-head', key: 'head' },
          h('span', { className: 'kc-star', 'aria-hidden': true }, '✦'),
          h('span', { className: 'kc-title' }, '编程小课堂'),
          h('span', { className: 'kc-sub' }, '两条线：学会指挥屏幕，也学会看懂地震'),
        ),
        ...tracks.map((track) => h(Track, { key: track.id, track, open })),
        h(Structure, { key: 'structure' }),
        h(
          'div',
          { className: 'kc-foot', key: 'foot' },
          '怎么上课：选一课 → 回答三个问题 → 看电脑上的图 → 上真机',
        ),
      );
    }

    // 会话里的「课程」页签：大纲常驻，随时可以挑下一课。
    // 选完写进草稿并切回对话页签，孩子按发送就开始。
    function Outline(props) {
      const preset = usePresetId(props);
      const open = props.openLesson;
      if (preset !== KIDCODE) return null;
      const pick = (trackId, number, name) => {
        open(trackId, number, name);
        try {
          if (typeof props.openView === 'function') props.openView('chat');
        } catch (error) {
          console.warn('[kidcode-courses] 切回对话失败', error);
        }
      };
      return h(
        'div',
        { className: 'kc-outline' },
        h('style', { key: 'style' }, styles),
        h(
          'div',
          { className: 'kc-head', key: 'head' },
          h('span', { className: 'kc-star', 'aria-hidden': true }, '✦'),
          h('span', { className: 'kc-title' }, '课程大纲'),
          h('span', { className: 'kc-sub' }, '选一课，回到对话开始'),
        ),
        ...tracks.map((track) => h(Track, { key: track.id, track, open: pick })),
      );
    }

    function CourseTab(props) {
      const preset = usePresetId(props);
      const open = props.openLesson;
      if (preset !== KIDCODE) return null;
      return h(
        React.Fragment,
        null,
        h('style', { key: 's' }, styles),
        h(
          'button',
          {
            key: 'b',
            type: 'button',
            className: 'kc-tab',
            title: '回到课程表',
            onClick: () => open(null, null, null),
          },
          h('span', { 'aria-hidden': true }, '✦'),
          '课程',
        ),
      );
    }

    return {
      inject: ['slots', 'uiWorkspace'],
      apply(ctx) {
        ctx.slots.inject('conversation.hero.options', () =>
          ctx.slots.register(
            { name: 'conversation.hero.options', id: 'kidcode-courses', order: 5 },
            (props) => h(Panel, { ...props, ctx, openLesson: makeOpener(ctx, props.inputActions) }),
          ),
        );
        // 对话 / 轨迹 旁边的「课程」页签。
        ctx.slots.inject('conversation.view', () =>
          ctx.slots.register(
            { name: 'conversation.view', id: 'kidcode-outline', order: 20, label: '课程' },
            (props) => h(Outline, { ...props, ctx, openLesson: makeOpener(ctx, props.inputActions) }),
          ),
        );

        ctx.slots.inject('conversation.session.header.actions', () =>
          ctx.slots.register(
            { name: 'conversation.session.header.actions', id: 'kidcode-course-tab', order: 5 },
            (props) => h(CourseTab, { ...props, ctx, openLesson: makeOpener(ctx, props.inputActions) }),
          ),
        );
      },
    };
  },
});
