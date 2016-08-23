Name:           metrics-reporter-config
Version:        3.0.2
Release:        1%{?dist}
Summary:        Manages config for metrics from Coda Hale’s Metrics library

License:        ASL 2.0
URL:            https://github.com/addthis/%{name}
Source0:        https://github.com/addthis/%{name}/archive/v%{version}.tar.gz

# remove optional dependencies references
# from files ReporterConfig.java SampleTest.java
Patch0:         removeOptionalDeps.patch

BuildArch:      noarch
# build parent
BuildRequires:  maven-local
BuildRequires:  mvn(org.slf4j:slf4j-api)
BuildRequires:  mvn(org.yaml:snakeyaml)
BuildRequires:  mvn(org.hibernate:hibernate-validator)
BuildRequires:  mvn(org.apache.commons:commons-lang3)
# build
BuildRequires:  mvn(com.addthis.metrics:reporter-config-base)
%if %{?fedora} < 24
BuildRequires:  mvn(com.codahale.metrics:metrics-ganglia)
BuildRequires:  mvn(com.codahale.metrics:metrics-graphite)
BuildRequires:  mvn(com.codahale.metrics:metrics-core)
%else
BuildRequires:  mvn(io.dropwizard.metrics:metrics-core)
BuildRequires:  mvn(io.dropwizard.metrics:metrics-ganglia)
BuildRequires:  mvn(io.dropwizard.metrics:metrics-graphite)
%endif
# testing parent
BuildRequires:  mvn(junit:junit)
BuildRequires:  mvn(org.slf4j:slf4j-simple)
BuildRequires:  mvn(com.google.guava:guava)
BuildRequires:  mvn(org.mockito:mockito-all)

# optional (not needed by cassandra therefore not packaged)
#BuildRequires:  mvn(com.readytalk:metrics-statsd-common)
#BuildRequires:  mvn(com.readytalk:metrics-statsd)
#BuildRequires:  mvn(io.github.hengyunabc:zabbix-sender)

%description
Coda Hale's Metrics package makes it easy to create useful metrics so you
know what is going on in production. In addition to showing up in the
normal Java places (JMX), Metrics supports an arbitrary number of Reporters
(where to send the application telemetry to make pretty graphs).
Ganglia and Graphite (or both) are among the most popular choices.

However, Metrics purposefully doesn't come with a kitchen sink of support for
every dependency injection or configuration tool yet devised by Java
developers. Metrics-Reporter-Config aims to provide a simple way to configure
and enable a set of Reporters that can be shared among applications. It
should fit most (say 90% of) use cases and avoid situations like a plethora
of subtly incompatible properties files.

%package        javadoc
Summary:        Javadoc for %{name}

%description javadoc
This package contains the API documentation for %{name}.

%prep
%setup -q

%mvn_alias :reporter-config3 :reporter-config
%mvn_file :reporter-config3 %{name}/reporter-config

# disable unnecessary module
%pom_disable_module reporter-config2

# remove parent (requires are preserved)
%pom_remove_parent 

# fix some versions because of missing parent
%pom_xpath_set "pom:version[text()='\${dep.slf4j.version}']" "1.7.14"
%pom_xpath_set "pom:version[text()='\${dep.guava.version}']" "19.0"

# missing org.junit
%pom_add_dep junit:junit::test

%if %{?fedora} < 24
%pom_change_dep io.dropwizard.metrics: com.codahale.metrics: reporter-config3/pom.xml
%endif

# remove optional dependencies
%pom_remove_dep com.readytalk:metrics-statsd-common reporter-config3
%pom_remove_dep com.readytalk:metrics3-statsd reporter-config3
%pom_remove_dep io.github.hengyunabc:zabbix-sender reporter-config3

# remove missing dependency (not needed for cassandra)
%pom_remove_dep com.izettle:dropwizard-metrics-influxdb reporter-config3

# remove files using optional dependencies
rm reporter-config3/src/main/java/com/addthis/metrics3/reporter/config/InfluxDBReporterConfig.java
rm reporter-config3/src/main/java/com/addthis/metrics3/reporter/config/ZabbixReporter.java
rm reporter-config3/src/main/java/com/addthis/metrics3/reporter/config/StatsDReporterConfig.java
rm reporter-config3/src/main/java/com/addthis/metrics3/reporter/config/ZabbixReporterConfig.java
rm reporter-config3/src/test/java/com/addthis/metrics3/reporter/config/StatsDReporterConfigTest.java

# removeOptionalDeps patch
%patch0 -p1

%build
%mvn_build -- -Dproject.build.sourceEncoding=UTF-8

%install
%mvn_install

%files -f .mfiles
%doc README.mdown
%license LICENSE NOTICE

%files javadoc -f .mfiles-javadoc
%license LICENSE NOTICE

%changelog
* Tue Aug 23 2016 Tomas Repik <trepik@redhat.com> - 3.0.2-1
- version update
- removed optional depenedencies that are not needed for cassandra

* Wed Mar 23 2016 Tomas Repik <trepik@redhat.com> - 3.0.0-1
- Initial RPM release

