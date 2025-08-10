import os
import json
import hashlib
from time import sleep
import curses

class EnhancedStudentGradeSystem:
    DATA_FILE = 'data.json'
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        # 初始化curses
        curses.curs_set(0)  # 隐藏光标
        curses.noecho()     # 不显示输入字符
        curses.cbreak()     # 立即响应按键
        
        # 初始化颜色
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # 标题颜色
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)  # 选中项颜色
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # 输入框颜色
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # 错误信息颜色
        
        # 初始化数据
        self.students = {}
        self.accounts = {
            'admin': {'password': self._hash_password('123456'), 'role': 'admin'}
        }
        self.current_user = None
        self._load_data()
    
    def _hash_password(self, password):
        """使用MD5加密密码"""
        return hashlib.md5(password.encode('utf-8')).hexdigest()
    
    def _load_data(self):
        """从文件加载数据"""
        try:
            with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.students = data.get('students', {})
                self.accounts = data.get('accounts', {
                    'admin': {'password': self._hash_password('123456'), 'role': 'admin'}
                })
        except FileNotFoundError:
            pass
        except Exception as e:
            self._show_message(f"加载数据失败: {e}", 2, curses.color_pair(4))
    
    def _save_data(self):
        """保存数据到文件"""
        try:
            data = {
                'students': self.students,
                'accounts': self.accounts
            }
            with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self._show_message(f"保存数据失败: {e}", 2, curses.color_pair(4))
    
    def _show_message(self, message, delay=1, color_pair=None):
        """显示消息并暂停"""
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        color = color_pair or curses.color_pair(1)
        self.stdscr.addstr(h//2, (w - len(message))//2, message, color)
        self.stdscr.refresh()
        sleep(delay)
    
    def _draw_menu(self, title, options, selected_idx):
        """绘制菜单"""
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        
        # 绘制标题
        self.stdscr.addstr(2, (w - len(title))//2, title, curses.color_pair(1))
        
        # 绘制选项
        for idx, option in enumerate(options):
            x = (w - len(option))//2
            y = h//2 - len(options)//2 + idx + 2  # 增加垂直间距
            
            if idx == selected_idx:
                self.stdscr.addstr(y, x, option, curses.color_pair(2))
            else:
                self.stdscr.addstr(y, x, option)
        
        # 绘制底部提示
        help_text = "使用↑↓箭头选择，回车确认 | ESC返回"
        self.stdscr.addstr(h-2, (w - len(help_text))//2, help_text, curses.color_pair(1))
        self.stdscr.refresh()
    
    def _get_menu_choice(self, title, options):
        """获取菜单选择"""
        selected_idx = 0
        while True:
            self._draw_menu(title, options, selected_idx)
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP:
                selected_idx = max(0, selected_idx - 1)
            elif key == curses.KEY_DOWN:
                selected_idx = min(len(options) - 1, selected_idx + 1)
            elif key == 10:  # 回车键
                return selected_idx
            elif key == 27:  # ESC键
                return -1
    
    def _get_input(self, prompt):
        """获取用户输入（解决重叠问题）"""
        curses.echo()
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        
        # 绘制输入框
        input_width = min(40, w - 10)  # 限制输入框宽度
        input_x = (w - input_width) // 2
        
        # 绘制提示
        self.stdscr.addstr(h//2 - 2, (w - len(prompt))//2, prompt, curses.color_pair(1))
        
        # 绘制输入区域背景
        for i in range(input_width):
            self.stdscr.addch(h//2, input_x + i, ' ', curses.color_pair(3))
        
        self.stdscr.move(h//2, input_x)
        self.stdscr.refresh()
        
        # 获取输入
        input_str = ""
        while True:
            ch = self.stdscr.getch()
            if ch == 10 or ch == 13:  # 回车键
                break
            elif ch == 27:  # ESC键
                curses.noecho()
                return None
            elif ch == curses.KEY_BACKSPACE or ch == 127:
                if len(input_str) > 0:
                    input_str = input_str[:-1]
                    self.stdscr.addch(h//2, input_x + len(input_str), ' ', curses.color_pair(3))
                    self.stdscr.move(h//2, input_x + len(input_str))
            elif len(input_str) < input_width and 32 <= ch <= 126:  # 可打印ASCII字符
                input_str += chr(ch)
                self.stdscr.addch(h//2, input_x + len(input_str) - 1, chr(ch))
            
            self.stdscr.refresh()
        
        curses.noecho()
        return input_str.strip()
    
    def _get_password_input(self, prompt="请输入密码: "):
        """获取密码输入(无回显)"""
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        
        # 绘制输入框
        input_width = min(40, w - 10)  # 限制输入框宽度
        input_x = (w - input_width) // 2
        
        # 绘制提示
        self.stdscr.addstr(h//2 - 2, (w - len(prompt))//2, prompt, curses.color_pair(1))
        
        # 绘制输入区域背景
        for i in range(input_width):
            self.stdscr.addch(h//2, input_x + i, ' ', curses.color_pair(3))
        
        self.stdscr.move(h//2, input_x)
        self.stdscr.refresh()
        
        password = []
        while True:
            ch = self.stdscr.getch()
            if ch == 10 or ch == 13:  # 回车键
                break
            elif ch == 27:  # ESC键
                return None
            elif ch == curses.KEY_BACKSPACE or ch == 127:
                if password:
                    password.pop()
                    self.stdscr.addch(h//2, input_x + len(password), ' ', curses.color_pair(3))
                    self.stdscr.move(h//2, input_x + len(password))
            elif len(password) < input_width and 32 <= ch <= 126:  # 可打印ASCII字符
                password.append(chr(ch))
                self.stdscr.addch(h//2, input_x + len(password) - 1, '*')
            
            self.stdscr.refresh()
        
        return ''.join(password)
    
    def _verify_admin_password(self):
        """验证管理员密码"""
        password = self._get_password_input("请输入管理员密码验证: ")
        if password is None:  # ESC键
            return False
        
        return self.accounts['admin']['password'] == self._hash_password(password)
    
    def login(self):
        """用户登录"""
        while True:
            username = self._get_input("请输入用户名: ")
            if username is None:  # ESC键
                return False
            
            password = self._get_password_input()
            if password is None:  # ESC键
                return False
            
            if username in self.accounts and \
               self.accounts[username]['password'] == self._hash_password(password):
                self.current_user = username
                self._show_message(f"登录成功! 欢迎{username}", 1)
                return True
            else:
                retry = self._show_confirm("用户名或密码错误! 是否重试? (Y/N)")
                if not retry:
                    return False
    
    def _show_confirm(self, message):
        """显示确认对话框"""
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        
        self.stdscr.addstr(h//2 - 1, (w - len(message))//2, message, curses.color_pair(1))
        self.stdscr.addstr(h//2 + 1, (w - 10)//2, "[Y] 是  [N] 否", curses.color_pair(1))
        self.stdscr.refresh()
        
        while True:
            key = self.stdscr.getch()
            if key == ord('y') or key == ord('Y'):
                return True
            elif key == ord('n') or key == ord('N') or key == 27:  # ESC键
                return False
    
    def logout(self):
        """用户登出"""
        self.current_user = None
        self._show_message("已成功登出", 1)
    
    def change_password(self):
        """修改密码"""
        if not self.current_user:
            self._show_message("请先登录!", 1)
            return
        
        while True:
            if self.current_user == 'admin':
                # 管理员修改其他用户密码
                username = self._get_input("请输入要修改密码的用户名(ESC返回): ")
                if username is None:  # ESC键
                    return
                
                if username not in self.accounts:
                    self._show_message("该用户不存在!", 1)
                    continue
                
                new_password = self._get_password_input("请输入新密码(ESC返回): ")
                if new_password is None:  # ESC键
                    continue
                
                self.accounts[username]['password'] = self._hash_password(new_password)
                self._save_data()
                self._show_message(f"用户{username}的密码已重置", 1)
                return
            else:
                # 学生修改自己的密码
                old_password = self._get_password_input("请输入原密码(ESC返回): ")
                if old_password is None:  # ESC键
                    return
                
                if self.accounts[self.current_user]['password'] != self._hash_password(old_password):
                    self._show_message("原密码错误!", 1)
                    continue
                
                new_password = self._get_password_input("请输入新密码(ESC返回): ")
                if new_password is None:  # ESC键
                    continue
                
                confirm_password = self._get_password_input("请再次输入新密码(ESC返回): ")
                if confirm_password is None:  # ESC键
                    continue
                
                if new_password == confirm_password:
                    self.accounts[self.current_user]['password'] = self._hash_password(new_password)
                    self._save_data()
                    self._show_message("密码修改成功!", 1)
                    return
                else:
                    self._show_message("两次输入的新密码不一致!", 1)
    
    def add_student_account(self, student_id, name):
        """添加学生账户"""
        if student_id not in self.accounts:
            self.accounts[student_id] = {
                'password': self._hash_password('s123456'),
                'role': 'student'
            }
    
    def add_student(self):
        """添加学生信息(仅管理员)"""
        if not self._check_admin():
            return
        
        while True:
            student_id = self._get_input("请输入学号(ESC返回): ")
            if student_id is None:  # ESC键
                return
            
            if student_id in self.students:
                self._show_message("该学号已存在!", 1)
                continue
            
            name = self._get_input("请输入姓名(ESC返回): ")
            if name is None:  # ESC键
                return
            
            chinese = self._get_input("请输入语文成绩(ESC返回): ")
            if chinese is None:  # ESC键
                return
            
            math = self._get_input("请输入数学成绩(ESC返回): ")
            if math is None:  # ESC键
                return
            
            english = self._get_input("请输入英语成绩(ESC返回): ")
            if english is None:  # ESC键
                return
            
            try:
                chinese = float(chinese)
                math = float(math)
                english = float(english)
            except ValueError:
                self._show_message("请输入有效的数字成绩!", 1)
                continue
            
            total = chinese + math + english
            average = total / 3
            
            self.students[student_id] = {
                'name': name,
                'chinese': chinese,
                'math': math,
                'english': english,
                'total': total,
                'average': average
            }
            
            # 自动创建学生账户
            self.add_student_account(student_id, name)
            self._save_data()
            self._show_message(f"学生{name}添加成功! 初始密码为s123456", 2)
            return
    
    def delete_student(self):
        """删除学生信息(仅管理员)"""
        if not self._check_admin():
            return
        
        while True:
            student_id = self._get_input("请输入要删除的学生学号(ESC返回): ")
            if student_id is None:  # ESC键
                return
            
            if student_id in self.students:
                name = self.students[student_id]['name']
                del self.students[student_id]
                
                # 同时删除账户
                if student_id in self.accounts:
                    del self.accounts[student_id]
                
                self._save_data()
                self._show_message(f"学生{name}(学号:{student_id})已删除", 1)
                return
            else:
                self._show_message("未找到该学号的学生!", 1)
    
    def query_student(self):
        """查询学生信息"""
        if not self.current_user:
            self._show_message("请先登录!", 1)
            return
        
        while True:
            if self.current_user == 'admin':
                # 管理员可以查询任何学生
                student_id = self._get_input("请输入要查询的学生学号(ESC返回): ")
                if student_id is None:  # ESC键
                    return
            else:
                # 学生只能查询自己的信息
                student_id = self.current_user
            
            student = self.students.get(student_id)
            if student:
                self.stdscr.clear()
                h, w = self.stdscr.getmaxyx()
                
                info = [
                    f"学号: {student_id}",
                    f"姓名: {student['name']}",
                    f"语文: {student['chinese']}",
                    f"数学: {student['math']}",
                    f"英语: {student['english']}",
                    f"总分: {student['total']}",
                    f"平均分: {student['average']:.2f}"
                ]
                
                for i, line in enumerate(info):
                    self.stdscr.addstr(h//2 - len(info)//2 + i, (w - len(line))//2, line)
                
                self.stdscr.addstr(h-2, (w - 20)//2, "按任意键继续...", curses.color_pair(1))
                self.stdscr.refresh()
                self.stdscr.getch()
                return
            else:
                retry = self._show_confirm("未找到该学号的学生! 是否重试? (Y/N)")
                if not retry:
                    return
    
    def update_student(self):
        """修改学生成绩(仅管理员)"""
        if not self._check_admin():
            return
        
        while True:
            student_id = self._get_input("请输入要修改的学生学号(ESC返回): ")
            if student_id is None:  # ESC键
                return
            
            if student_id not in self.students:
                self._show_message("未找到该学号的学生!", 1)
                continue
            
            # 显示当前信息
            student = self.students[student_id]
            self.stdscr.clear()
            h, w = self.stdscr.getmaxyx()
            
            info = [
                "当前学生信息:",
                f"学号: {student_id}",
                f"姓名: {student['name']}",
                f"语文: {student['chinese']}",
                f"数学: {student['math']}",
                f"英语: {student['english']}",
                "",
                "请输入新的成绩(留空则保持不变, ESC返回):"
            ]
            
            for i, line in enumerate(info):
                self.stdscr.addstr(h//2 - len(info)//2 + i, (w - len(line))//2, line)
            
            self.stdscr.refresh()
            
            # 获取新成绩
            chinese = self._get_input("语文成绩: ")
            if chinese is None:  # ESC键
                return
            
            math = self._get_input("数学成绩: ")
            if math is None:  # ESC键
                return
            
            english = self._get_input("英语成绩: ")
            if english is None:  # ESC键
                return
            
            try:
                if chinese:
                    student['chinese'] = float(chinese)
                if math:
                    student['math'] = float(math)
                if english:
                    student['english'] = float(english)
                
                # 重新计算总分和平均分
                student['total'] = student['chinese'] + student['math'] + student['english']
                student['average'] = student['total'] / 3
                
                self._save_data()
                self._show_message("学生信息更新成功!", 1)
                return
            except ValueError:
                self._show_message("请输入有效的数字成绩!", 1)
    
    def show_all_students(self):
        """显示所有学生信息(仅管理员)"""
        if not self._check_admin():
            return
        
        if not self.students:
            self._show_message("当前没有学生信息!", 1)
            return
        
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        
        title = "所有学生信息:"
        header = f"{'学号':<10}{'姓名':<10}{'语文':<8}{'数学':<8}{'英语':<8}{'总分':<8}{'平均分':<8}"
        separator = "-" * 60
        
        # 计算显示范围
        start_idx = 0
        max_lines = h - 6  # 保留空间给标题和底部提示
        
        while True:
            self.stdscr.clear()
            
            # 绘制标题
            self.stdscr.addstr(2, (w - len(title))//2, title, curses.color_pair(1))
            
            # 绘制表头
            self.stdscr.addstr(4, (w - len(header))//2, header)
            self.stdscr.addstr(5, (w - len(separator))//2, separator)
            
            # 绘制学生信息
            student_ids = list(self.students.keys())
            for i in range(start_idx, min(start_idx + max_lines, len(student_ids))):
                student_id = student_ids[i]
                info = self.students[student_id]
                line = f"{student_id:<10}{info['name']:<10}{info['chinese']:<8.1f}{info['math']:<8.1f}" \
                       f"{info['english']:<8.1f}{info['total']:<8.1f}{info['average']:<8.2f}"
                self.stdscr.addstr(6 + i - start_idx, (w - len(line))//2, line)
            
            # 绘制底部提示
            help_text = "↑↓浏览 | ESC返回"
            if len(self.students) > max_lines:
                help_text += f" ({start_idx+1}-{min(start_idx + max_lines, len(self.students))}/{len(self.students)})"
            self.stdscr.addstr(h-2, (w - len(help_text))//2, help_text, curses.color_pair(1))
            
            self.stdscr.refresh()
            
            # 处理按键
            key = self.stdscr.getch()
            if key == curses.KEY_UP and start_idx > 0:
                start_idx -= 1
            elif key == curses.KEY_DOWN and start_idx + max_lines < len(self.students):
                start_idx += 1
            elif key == 27:  # ESC键
                return
    
    def _check_admin(self):
        """检查当前用户是否为管理员"""
        if not self.current_user:
            self._show_message("请先登录!", 1)
            return False
        if self.current_user != 'admin':
            self._show_message("只有管理员可以执行此操作!", 1)
            return False
        return True
    
    def main_menu(self):
        """主菜单"""
        while True:
            if self.current_user == 'admin':
                title = "管理员菜单"
                options = [
                    "1. 添加学生信息",
                    "2. 删除学生信息",
                    "3. 查询学生信息",
                    "4. 修改学生成绩",
                    "5. 显示所有学生信息",
                    "6. 重置学生密码",
                    "7. 修改密码",
                    "8. 退出登录",
                    "0. 退出系统"
                ]
            else:
                title = "学生菜单"
                options = [
                    "1. 查询我的成绩",
                    "2. 修改密码",
                    "3. 退出登录",
                    "0. 退出系统"
                ]
            
            choice = self._get_menu_choice(title, options)
            if choice == -1:  # ESC键
                if self._show_confirm("确定要返回登录界面吗? (Y/N)"):
                    self.logout()
                    return
            
            if self.current_user == 'admin':
                if choice == 0:
                    self.add_student()
                elif choice == 1:
                    self.delete_student()
                elif choice == 2:
                    self.query_student()
                elif choice == 3:
                    self.update_student()
                elif choice == 4:
                    self.show_all_students()
                elif choice == 5:
                    self.change_password()  # 管理员重置密码
                elif choice == 6:
                    self.change_password()  # 修改自己的密码
                elif choice == 7:
                    self.logout()
                    return
                elif choice == 8:
                    if self._show_confirm("确定要退出系统吗? (Y/N)"):
                        if self._verify_admin_password():
                            self._save_data()
                            return True  # 退出系统
                        else:
                            self._show_message("管理员密码验证失败!", 1, curses.color_pair(4))
            else:
                if choice == 0:
                    self.query_student()
                elif choice == 1:
                    self.change_password()
                elif choice == 2:
                    self.logout()
                    return
                elif choice == 3:
                    if self._show_confirm("确定要退出系统吗? (Y/N)"):
                        self._save_data()
                        return True  # 退出系统

def main(stdscr):
    system = EnhancedStudentGradeSystem(stdscr)
    
    # 登录循环
    while True:
        if system.login():
            # 主菜单循环
            should_exit = system.main_menu()
            if should_exit:
                break
        else:
            # 登录失败后的选项
            options = ["1. 重试", "0. 退出"]
            choice = system._get_menu_choice("登录失败", options)
            if choice == 0:  # 重试
                continue
            elif choice == 1:  # 退出
                break
    
    # 退出前清屏
    stdscr.clear()
    stdscr.addstr(0, 0, "感谢使用成绩管理系统，再见!")
    stdscr.refresh()
    sleep(1)

if __name__ == "__main__":
    curses.wrapper(main)
