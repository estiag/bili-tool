Vue.component('right-menu', {
  template:
    '<ul v-show="visible" ref="rightMenu" class="fixed p-1 shadow-sm menu dropdown-content z-10 bg-base-300 rounded-box w-40">' +
    '  <li><button @click="goback">返回</button></li>' +
    '  <li><button @click="refresh">刷新</button></li>' +
    '  <li><button @click="copy">复制</button></li>' +
    '  <li><button @click="paste">粘贴</button></li>' +
    '</ul>',
  data: function () {
    return {
      visible: false,
      x: 0,
      y: 0,
      lastFocusedElement: null,
    }
  },
  mounted: function () {
    var app = this
    document.addEventListener('contextmenu', function (event) {
      event.preventDefault()
      var x = event.clientX + window.scrollX
      var y = event.clientY + window.scrollY
      app.$refs.rightMenu.style.left = x + 'px'
      app.$refs.rightMenu.style.top = y + 'px'
      app.showMenu()
    })
    document.addEventListener('click', function (event) {
      app.closeMenu()
    })
  },
  methods: {
    showMenu: function () {
      this.lastFocusedElement = document.activeElement
      this.visible = true
    },
    closeMenu: function () {
      this.visible = false
    },
    copy: function () {
      const selectedText = window.getSelection().toString()
      if (selectedText) {
        localStorage.setItem('clipboardData', selectedText)
        try {
          navigator.clipboard
            .writeText(selectedText)
            .then(() => {})
            .catch((err) => {
              console.error('复制失败:', err)
            })
        } catch (err) {
          // 兼容旧浏览器
          const textarea = document.createElement('textarea')
          textarea.value = selectedText
          document.body.appendChild(textarea)
          textarea.select()
          document.execCommand('copy')
          document.body.removeChild(textarea)
        }
      }
    },
    paste: function (event) {
      try {
        if (!navigator.clipboard.readText) { 
          this.lastFocusedElement.focus()
          document.execCommand('paste')
        }
        navigator.clipboard
          .readText()
          .then((text) => {
            if (this.lastFocusedElement) {
              this.insterText(this.lastFocusedElement, text)
            }
          })
          .catch((err) => {
            console.error('粘贴失败:', err)
          })
      } catch (err) {
        var clipboardData = localStorage.getItem('clipboardData')
        if (clipboardData) {
          if (this.lastFocusedElement) {
            this.insterText(this.lastFocusedElement, clipboardData)
          }
        }
      }
    },
    insterText: function (obj, str) {
      if (document.selection) {
        var sel = document.selection.createRange()
        sel.text = str
      } else if (
        typeof obj.selectionStart == 'number' &&
        typeof obj.selectionEnd == 'number'
      ) {
        var startPos = obj.selectionStart
        var endPos = obj.selectionEnd
        var cursorPos = startPos
        var tmpStr = obj.value
        obj.value =
          tmpStr.substring(0, startPos) +
          str +
          tmpStr.substring(endPos, tmpStr.length)
      } else {
        obj.value += str
      }
    },
    refresh: function () {
      location.reload()
    },
    goback: function () {
      history.go(-1)
    },
  },
})
