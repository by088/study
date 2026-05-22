<template>
  <main class="shell">
    <header>
      <h1>StudySeatOps</h1>
      <nav>
        <RouterLink to="/">学生端</RouterLink>
        <RouterLink to="/admin">管理端</RouterLink>
      </nav>
    </header>
    <RouterView />
  </main>
</template>

<style scoped>
.shell {
  max-width: 980px;
  margin: 0 auto;
  padding: 24px;
  font-family: "Segoe UI", "PingFang SC", sans-serif;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
nav {
  display: flex;
  gap: 16px;
}
</style>
