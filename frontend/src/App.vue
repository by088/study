<template>
  <main class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">S</div>
        <div>
          <h1>StudySeatOps</h1>
          <p>自习座位预约系统</p>
        </div>
      </div>

      <nav class="nav">
        <RouterLink to="/" class="nav-link">学生预约</RouterLink>
        <RouterLink to="/admin" class="nav-link">运营管理</RouterLink>
      </nav>

      <div class="sidebar-footer">
        <span>API</span>
        <strong>localhost:8001</strong>
      </div>
    </aside>

    <section class="workspace">
      <RouterView />
    </section>
  </main>
</template>

<style>
:root {
  color: #172033;
  background: #eef2f7;
  font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
  background:
    linear-gradient(135deg, rgba(38, 92, 83, 0.08), transparent 34%),
    linear-gradient(315deg, rgba(190, 84, 55, 0.08), transparent 28%),
    #eef2f7;
}

button,
input,
select {
  font: inherit;
}

button {
  cursor: pointer;
}
</style>

<style scoped>
.app-shell {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  min-height: 100vh;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 24px 18px;
  background: #172033;
  color: #fff;
}

.brand {
  display: flex;
  gap: 12px;
  align-items: center;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.14);
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 8px;
  background: #e1b45f;
  color: #172033;
  font-weight: 900;
  font-size: 22px;
}

h1 {
  margin: 0;
  font-size: 18px;
}

p {
  margin: 4px 0 0;
  color: rgba(255, 255, 255, 0.68);
  font-size: 13px;
}

.nav {
  display: grid;
  gap: 8px;
  margin-top: 24px;
}

.nav-link {
  display: block;
  padding: 12px 14px;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.72);
  text-decoration: none;
  font-weight: 700;
}

.nav-link.router-link-active {
  background: #eef2f7;
  color: #172033;
}

.sidebar-footer {
  margin-top: auto;
  padding: 14px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.08);
  display: grid;
  gap: 4px;
  font-size: 13px;
}

.sidebar-footer span {
  color: rgba(255, 255, 255, 0.58);
}

.workspace {
  min-width: 0;
  padding: 28px;
}

@media (max-width: 820px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
    height: auto;
    padding: 16px;
  }

  .nav {
    grid-template-columns: 1fr 1fr;
    margin-top: 16px;
  }

  .sidebar-footer {
    display: none;
  }

  .workspace {
    padding: 16px;
  }
}
</style>
