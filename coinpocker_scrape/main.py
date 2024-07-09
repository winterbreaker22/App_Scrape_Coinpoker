import time
import csv
from pywinauto import Application, timings, mouse
from pywinauto.timings import TimeoutError
timings.Timings.window_find_timeout = 60

login_email=""
login_pwd=""

class AppScraper():
    def __init__(self) -> None:
        try:
            self.app = Application(backend='uia').start("C:\\CoinPoker\\Lobby.exe")
            time.sleep(10)
        except:
            Application().connect(title="GameWindow").kill()
            self.app = Application(backend='uia').start("C:\\CoinPoker\\Lobby.exe")
            time.sleep(10)
        self.dlg = self.get_dlg()
    
    def get_dlg(self, title="GameWindow", class_name='Lobby'):
        try:
            dlg = self.app.window(title = "GameWindow", class_name = 'Lobby')
            dlg.wait('visible', timeout=60)
            dlg.wait('ready', timeout=60)
            return dlg
        except TimeoutError:
            print("Timed out waiting for the window to be ready")
            return None
    
    def mouse_scroll(self):
        table = self.dlg.child_window(
            auto_id = 'Lobby.captionWrapper.wrapper.content.TabForm.scrollbarContainer.ListBox',
            control_type = 'Table',
            class_name='CustomTableView'
        )
        mouse.scroll(coords=(table.rectangle().mid_point().x, table.rectangle().mid_point().y), wheel_dist=-4)
        self.dlg = self.get_dlg()
    
    def login_func(self):
        try:
            email_input= self.dlg.child_window(
                auto_id = "Lobby.captionWrapper.wrapper.content.LoginForm.stackedWidget.loginPage.rightSideTopWidget.loginAndRemindStack.loginPartPage.scrollArea.qt_scrollarea_viewport.scrollAreaWidgetContents.loginUserName",
                control_type="Edit",
                class_name="QLineEdit"
                )
            email_input.set_text(login_email)
            
            pwd_input = self.dlg.child_window(
                auto_id = "Lobby.captionWrapper.wrapper.content.LoginForm.stackedWidget.loginPage.rightSideTopWidget.loginAndRemindStack.loginPartPage.scrollArea.qt_scrollarea_viewport.scrollAreaWidgetContents.loginPassword",
                control_type="Edit",
                class_name="QLineEdit"
                )
            pwd_input.set_text(login_pwd)
            
            login_btn = self.dlg.child_window(
                auto_id = "Lobby.captionWrapper.wrapper.content.LoginForm.stackedWidget.loginPage.rightSideTopWidget.loginAndRemindStack.loginPartPage.scrollArea.qt_scrollarea_viewport.scrollAreaWidgetContents.loginButtonPlaceholder.errorField.loginButton",
                control_type="Button",
                class_name="QPushButton",
            )
            login_btn.click()
            
            time.sleep(5)
            self.dlg = self.get_dlg()
            return True
        except Exception as e:
            print ("Error : " + str(e))
            return False
        
    def get_content(self):
        temp = []
        # with resolution 1366 * 768
        for _ in range(30):
            self.mouse_scroll()
            table = self.dlg.child_window(
                auto_id = 'Lobby.captionWrapper.wrapper.content.TabForm.scrollbarContainer.ListBox',
                control_type = 'Table',
                class_name='CustomTableView'
            )
            # temp.extend(table.descendants())
            for elem in table.descendants():
                temp.append(elem)

            temp = self.remove_duplicated_value(temp)
        
        row = dict()
        for index, item in enumerate(temp[9:]):
            row[self.switch_key((index + 1) % 7)] = item.element_info.rich_text
            if(((index + 1) % 7) == 0):
                print(row)
                self.save2csv(row)
                row = dict()
            
    def switch_key(self, index_v):
        switch = {
            1: "Date",
            2: "Name",
            3: "TYPE",
            4: "BUY-IN",
            5: "PRIZE",
            6: "PLAYERS",
            0: "STATUS"
        }
        return switch.get(index_v, "TEMP")

    def remove_duplicated_value(self, temp):
        seen = set()
        unique_array = []
        for item in temp:
            if item not in seen:
                unique_array.append(item)
                seen.add(item) 
        return unique_array
    
    def save2csv(self, data):
        with open('result.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(data)
    
    def start(self):
        if self.login_func():
            try:
                self.get_content()
                        
            except Exception as e:
                print(e)
                self.app.kill()
        else:
            print('Login action is failed.')

def main():
    tool = AppScraper()
    
    tool.start()

if __name__ == '__main__':
    main()  