from csscompressor import compress
import os

def minify_css(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # Minify the CSS
    minified_css = compress(css_content)
    
    # Write the minified CSS to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(minified_css)
    
    # Get file sizes
    original_size = os.path.getsize(input_file)
    minified_size = os.path.getsize(output_file)
    savings = original_size - minified_size
    
    print(f"Original size: {original_size/1024:.1f} KB")
    print(f"Minified size: {minified_size/1024:.1f} KB")
    print(f"Savings: {savings/1024:.1f} KB ({savings/original_size*100:.1f}% reduction)")

if __name__ == "__main__":
    input_css = "static/css/main_blue_theme.css"
    output_css = "static/css/main_blue_theme.min.css"
    
    minify_css(input_css, output_css)
