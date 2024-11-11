import time
import csv
from pywinauto import Application, timings, mouse
from pywinauto.timings import TimeoutError, wait_until
timings.Timings.window_find_timeout = 60
import schedule

login_email="joejames8123@gmail.com"
login_pwd="qwer1234QWER!@#$"

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
        self.data = []
        self.additional_data = []
    
    def get_dlg(self, title="GameWindow", class_name='Lobby'):
        try:
            dlg = self.app.window(title = "GameWindow", class_name = 'Lobby')
            dlg.wait('visible', timeout=60)
            dlg.wait('ready', timeout=60)
            return dlg
        except TimeoutError:
            print("Timed out waiting for the window to be ready")
            return None
    
    def get_detail_dlgs(self, title="GameWindow", class_name = "TourLobby"):
        try:
            dlgs = self.app.windows(title = title, class_name=class_name)
            return dlgs
        except Exception as e:
            print(e)
            print("Timed out waiting for the window to be ready")
            return None
    
    def get_detail_dlg(self, title="GameWindow", class_name = "TourLobby"):
        try:
            dlg = self.app.windows(title = title, class_name=class_name)
            dlg.wait('visible', timeout=60)
            dlg.wait('ready', timeout=60)
            return dlg
        except:
            print("Timed out waiting for the window to be ready")
            return None
    
    def mouse_scroll(self, value):
        table = self.dlg.child_window(
            auto_id = 'Lobby.captionWrapper.wrapper.content.TabForm.scrollbarContainer.ListBox',
            control_type = 'Table',
            class_name='CustomTableView'
        )
        mouse.scroll(coords=(table.rectangle().mid_point().x, table.rectangle().mid_point().y), wheel_dist=value)
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

            # tab_element = self.dlg.child_window(
            #     auto_id = "Lobby.captionWrapper.wrapper.tabs.SelectBar.Button",
            #     control_type = "CheckBox",
            #     class_name ="ButtonWithBadge",
            #     name = "Tournaments"
            # )
            # tab_element.click()
            # self.dlg = self.get_dlg()
            return True
        except Exception as e:
            print ("Error : " + str(e))
            return False
        
    def get_content(self):
        temp = []
        # with resolution 1366 * 768
        for _ in range(30):
            table = self.dlg.child_window(
                auto_id = 'Lobby.captionWrapper.wrapper.content.TabForm.scrollbarContainer.ListBox',
                control_type = 'Table',
                class_name='CustomTableView'
            )
            # temp.extend(table.descendants())
            for elem in table.descendants():
                temp.append(elem)

            temp = self.remove_duplicated_value(temp)
            self.mouse_scroll(-4)
        
        self.dlg.type_keys('{PGUP}')
        row = dict()
        for index, item in enumerate(temp[9:]):
            row[self.switch_key((index + 1) % 7)] = item.element_info.rich_text
            if(((index + 1) % 7) == 1):
                table = self.dlg.child_window(
                    auto_id = 'Lobby.captionWrapper.wrapper.content.TabForm.scrollbarContainer.ListBox',
                    control_type = 'Table',
                    class_name='CustomTableView'
                )

                time.sleep(1)
                
                if len(self.data) > 1 and len(self.data) % 3 == 0:
                    dlgs = self.get_detail_dlgs()
                    for dlg in dlgs:
                        dlg.restore()
                        dlg.set_focus()
                        add_row = dict()
                        elements = dlg.descendants()
                        name = None
                        info = None
                        close_btn = None
                        for element in elements:
                            if element.element_info.element.CurrentAutomationId == "TourLobby.Header.Description":
                                name = element.element_info.rich_text
                        add_row['name'] = name
                        for element in elements:
                            if element.element_info.element.CurrentAutomationId == "TourLobby.widget_main.Summary.tabInfo.containerBlockAwardList.blockAwardList.blockAwardListContent.AwardList":
                                info = element.element_info.rich_text
                        add_row['Additional Info'] = info
                        for element in elements:
                            if element.element_info.element.CurrentAutomationId == "TourLobby.WindowCaption.ButtonClose":
                                close_btn = element
                        close_btn.click()
                        self.additional_data.append(add_row)
                        self.save2csv('additional.csv', add_row)
                        print(add_row)
                table.type_keys('{ENTER}')

                item.click_input()
                
                table.type_keys('{DOWN}')
                
            if(((index + 1) % 7) == 0):
                self.data.append(row)
                print(row)
                self.save2csv('result.csv', row)
                row = dict()
        
        # for info in self.additional_data:
        for drow in self.data:
            # if drow['Name'] == info[name]:
                drow['Additional Info'] = self.get_additional_info(drow['name'])
                self.save2csv('final.csv', drow)
    def get_additional_info(self, name):
        for info in self.additional_data: 
            if info['name'] == name:
                return info['Additional Info']           
        
    def is_element_visible(self, item):
        try:
            return item.is_visible()
        except Exception:
            return False
    
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
    
    def save2csv(self,filename, data):
        with open(filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(data)
    
    def clear_csv_file(self, file_path):
        with open(file_path, 'w', newline='') as file:
            # Just open the file in 'w' mode to clear its contents
            pass
        print(f"Cleared contents of {file_path}")

    def start(self):
        self.clear_csv_file('result.csv')
        self.clear_csv_file('additional.csv')
        if self.login_func():
            try:
                self.get_content()
                        
            except Exception as e:
                print(e)
                self.app.kill()
        else:
            print('Login action is failed.')

    def close_app(self):
        try:
            self.app.kill()
            print("Application closed successfully.")
        except Exception as e:
            print(f"Failed to close application: {e}")

def main():
    tool = AppScraper()
    
    tool.start()

    tool.close_app()

if __name__ == '__main__':
    main()
    schedule.every(2).hours.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1) 