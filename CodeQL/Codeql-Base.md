# Codeql

## 环境搭建

- VScode下安装插件**Codeql**,直接安装即可安装完毕后VScode中有如下界面。

![](https://tcs.teambition.net/storage/31235491ab584eff0e1b254ee6083a690b2a?Signature=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJBcHBJRCI6IjU5Mzc3MGZmODM5NjMyMDAyZTAzNThmMSIsIl9hcHBJZCI6IjU5Mzc3MGZmODM5NjMyMDAyZTAzNThmMSIsIl9vcmdhbml6YXRpb25JZCI6IjYwNWM4MmEwNTVlNGVkNjVhY2JkOTk1YSIsImV4cCI6MTYxNzYxMDIwMiwiaWF0IjoxNjE3MDA1NDAyLCJyZXNvdXJjZSI6Ii9zdG9yYWdlLzMxMjM1NDkxYWI1ODRlZmYwZTFiMjU0ZWU2MDgzYTY5MGIyYSJ9.gJEKB-KtKPrNWaNOB7Qea6S1lkcmJK5m1qMb5lmK7aI&download=vscode-plugin.jpg "")

- 下载最新的Codeql Cli  [https://github.com/github/codeql-cli-binaries/releases](https://github.com/github/codeql-cli-binaries/releases)

- 配置Codeql插件  指定cli可执行文件位置。如果是Windows下，那么这里就是对应Cli目录下的codeql.cmd文件

![](https://tcs.teambition.net/storage/3123dce2e8fcee853d29967b85c92319dbb2?Signature=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJBcHBJRCI6IjU5Mzc3MGZmODM5NjMyMDAyZTAzNThmMSIsIl9hcHBJZCI6IjU5Mzc3MGZmODM5NjMyMDAyZTAzNThmMSIsIl9vcmdhbml6YXRpb25JZCI6IjYwNWM4MmEwNTVlNGVkNjVhY2JkOTk1YSIsImV4cCI6MTYxNzYxMDIwOCwiaWF0IjoxNjE3MDA1NDA4LCJyZXNvdXJjZSI6Ii9zdG9yYWdlLzMxMjNkY2UyZThmY2VlODUzZDI5OTY3Yjg1YzkyMzE5ZGJiMiJ9.lA5FxONYw94RVGTKAdub232BJKfNXWbFhGP7iYEcX48&download=setting.jpg "")

- 下载项目vscode-codeql-starter  [https://github/vscode-codeql-starter](https://github/vscode-codeql-starter)  可以直接**git clone --recursive**一步到位

## How to use

- 首先在Vscode中打开vscode-codeql-starter内的vscode-codeql-starter.code-workspace,这就是之后的开发环境。

- 除此之外，我们还需要导入Codeql database，这个databse可以直接从网上下，当然也可以自己创建。**官方文档**[https://codeql.github.com/docs/codeql-cli/creating-codeql-databases/](https://codeql.github.com/docs/codeql-cli/creating-codeql-databases/)

    - 对于C/C++、java这种编译型语言，在创建database时还要指定--command编译程序,如果不指定command，则会使用默认的编译指令（大概率会有点问题）。 如（***在源码文件夹内创建database***）smt:codeql database create [database name] --language=[...] --command=[...]codeql database create ctest --language=cpp --command='gcc t.cpp t'

    - 对于Javascript、python这种脚本型语言，则可以省略编译这个环节smt:codeql database create [database name] --language=[...]codeql database create jstest --language=javascript

- 有了database即可选定database，开始Code了！

- 编写的.ql文件在workstation下编写，有对应的qlpack.yml和queries.xml文件。（在其他文件夹写，会报缺少qlpack.yml文件）

## 基本原理

对于需要编译的语言而言，CodeQL收集编译过程中产生的信息，而不关心代码是怎么被编译的，或者收集到的信息是否完整。即使项目在编译过程中中断、出错，或者部分代码没有被编译，CodeQL也能正常对已收集到的信息进行正确处理。同时，只要当前项目无法产生编译信息，即使项目的编译方式是被CodeQL所支持的，也无法正常生成数据库。

导致无法正常生成数据库的常见原因有：

1. 项目缺少依赖或代码出错

1. 项目编译命令或编译配置出错

1. 编译过程被跳过(上一次编译的缓存未清除等)

CodeQL需要代码编译过程中的信息，而不关注代码编译后生成的字节码文件。因此无法通过“将上一次编译好的字节码文件拷贝到原项目中”的方式来欺骗CodeQL生成数据库。对于在编译过程中没有编译到的代码也不会被存入数据库。即使项目的编译方式是被CodeQL所支持的，要使用CodeQL对其进行分析往往也需要重写配置文件。

**CodeQL透过编译过程生成数据库，CodeQL无法分析未被编译的代码。**

## Codeql数据库结构

目标database创建好后，目录结构为

- log/                  # 输出的日志信息

- db-cpp/               # 编译的数据库

- src.zip               # 编译所对应的目标源码

- codeql-database.yml   # 数据库相关配置

src.zip结构为：可以看是在编译过程中所有涉及的文件。

![](https://tcs.teambition.net/storage/31236efa0869907efe9057c14391572cfd75?Signature=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJBcHBJRCI6IjU5Mzc3MGZmODM5NjMyMDAyZTAzNThmMSIsIl9hcHBJZCI6IjU5Mzc3MGZmODM5NjMyMDAyZTAzNThmMSIsIl9vcmdhbml6YXRpb25JZCI6IjYwNWM4MmEwNTVlNGVkNjVhY2JkOTk1YSIsImV4cCI6MTYxNzYxMDIxOCwiaWF0IjoxNjE3MDA1NDE4LCJyZXNvdXJjZSI6Ii9zdG9yYWdlLzMxMjM2ZWZhMDg2OTkwN2VmZTkwNTdjMTQzOTE1NzJjZmQ3NSJ9.Jq3zo7s3mv1zaeUXZztyuKIAflMTv9QOfSvQGVdjG3U&download=src-tree.jpg "")

## 基本语法

```sql
import <language>

select "hello world"
```

```sql
from /* ... variable declarations ... */
where /* ... logical formulas ... */
select /* ... expressions ... */
```

## Reference:

- [https://paper.seebug.org/1324/#_3](https://paper.seebug.org/1324/#_3)

- [https://kiprey.github.io/2020/12/CodeQL-setup/](https://kiprey.github.io/2020/12/CodeQL-setup/)

- [https://codeql.github.com/docs/](https://codeql.github.com/docs/)

