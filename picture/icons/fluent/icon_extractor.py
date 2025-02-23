import os

def extract_icons(icons_file_path, output_dir):
    """从.icons文件中提取SVG图标
    Args:
        icons_file_path: .icons文件的路径
        output_dir: 输出目录
    """
    with open(icons_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按行分割
    lines = content.split('\n')
    
    # 遍历每一行
    for line in lines:
        if not line.strip():
            continue
            
        # 分割图标名称和SVG内容
        if '////' in line:
            name, svg = line.split('////')
            name = name.strip()
            svg = svg.strip()
            
            # 替换颜色占位符
            svg = svg.replace('<<<COLOR_CODE>>>', 'currentColor')
            
            # 保存SVG文件
            output_path = os.path.join(output_dir, f'{name}.svg')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(svg)

if __name__ == '__main__':
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
    siui_path = os.path.join(project_root, 'PyQt-SiliconUI', 'siui', 'gui', 'icons', 'packages')
    
    # 提取常规图标
    extract_icons(
        os.path.join(siui_path, 'fluent_ui_icon_regular.icons'),
        current_dir
    )
    # 提取填充图标
    extract_icons(
        os.path.join(siui_path, 'fluent_ui_icon_filled.icons'),
        current_dir
    ) 