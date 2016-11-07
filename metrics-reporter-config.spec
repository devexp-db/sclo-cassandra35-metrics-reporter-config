%{?scl:%scl_package metrics-reporter-config}
%{!?scl:%global pkg_name %{name}}

Name:           %{?scl_prefix}metrics-reporter-config
Version:        3.0.3
Release:        2%{?dist}
Summary:        Manages config for metrics from Coda Hale’s Metrics library
License:        ASL 2.0
URL:            https://github.com/addthis/%{name}
Source0:        https://github.com/addthis/%{name}/archive/v%{version}.tar.gz

# remove optional dependencies references
# from files ReporterConfig.java SampleTest.java
Patch0:         remove_optional_deps.patch
# remove optional dependencies references only in SCL package
# from files ReporterConfig.java SampleTest.java
Patch1:         remove_SCL_optional_deps.patch

BuildArch:      noarch

# build parent
BuildRequires:  %{?scl_prefix_maven}maven-local
BuildRequires:  %{?scl_prefix_maven}apache-commons-lang3
BuildRequires:  %{?scl_prefix_java_common}slf4j%{?scl:-api}
BuildRequires:  %{?scl_prefix_java_common}snakeyaml
# use bean-validation-api instead of hibernate-validator
#BuildRequires:  mvn(org.hibernate:hibernate-validator)
BuildRequires:  %{?scl_prefix}bean-validation-api
# build
BuildRequires:  %{?scl_prefix}metrics
# optional dependencies for cassandra not needed
%{!?scl:BuildRequires:  metrics-ganglia
BuildRequires:  metrics-graphite}
# testing parent
BuildRequires:  %{?scl_prefix_java_common}junit
BuildRequires:  %{?scl_prefix_java_common}slf4j%{?scl:-simple}
BuildRequires:  %{?scl_prefix_java_common}guava
BuildRequires:  %{?scl_prefix_maven}mockito
%{?scl:Requires: %scl_runtime}

# optional missing dependencies
#BuildRequires:  mvn(com.readytalk:metrics-statsd-common)
#BuildRequires:  mvn(com.readytalk:metrics-statsd)
#BuildRequires:  mvn(io.github.hengyunabc:zabbix-sender)
#BuildRequires:  mvn(io.prometheus:simpleclient_pushgateway)
#BuildRequires:  mvn(io.prometheus:simpleclient_servlet)

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

%package javadoc
Summary:	Javadoc for %{name}

%description javadoc
This package contains the API documentation for %{name}.

%prep
%setup -q -n %{pkg_name}-%{version}

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
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

%if 0%{?fedora} < 24
# do not do this in SCL package
%{!?scl:%pom_change_dep io.dropwizard.metrics: com.codahale.metrics: reporter-config3/pom.xml}
%endif

# remove optional dependencies
%pom_remove_dep com.readytalk:metrics-statsd-common reporter-config3
%pom_remove_dep com.readytalk:metrics3-statsd reporter-config3
%pom_remove_dep io.github.hengyunabc:zabbix-sender reporter-config3

# remove optional dependencies only in SCL package
%{?scl:%pom_remove_dep io.dropwizard.metrics:metrics-ganglia reporter-config3
%pom_remove_dep io.dropwizard.metrics:metrics-graphite reporter-config3}

# replace hibernate-validator with bean-validation-api
%pom_remove_dep org.hibernate:hibernate-validator
%pom_add_dep javax.validation:validation-api

# remove missing dependencies (not needed for cassandra)
%pom_remove_dep com.izettle:dropwizard-metrics-influxdb reporter-config3
%pom_remove_dep io.prometheus:simpleclient_pushgateway reporter-config3
%pom_remove_dep io.prometheus:simpleclient_servlet reporter-config3

# remove files using optional dependencies
rm reporter-config3/src/main/java/com/addthis/metrics3/reporter/config/InfluxDBReporterConfig.java
rm reporter-config3/src/main/java/com/addthis/metrics3/reporter/config/ZabbixReporter.java
rm reporter-config3/src/main/java/com/addthis/metrics3/reporter/config/StatsDReporterConfig.java
rm reporter-config3/src/main/java/com/addthis/metrics3/reporter/config/ZabbixReporterConfig.java
rm -r reporter-config3/src/main/java/com/addthis/metrics3/reporter/config/prometheus
rm reporter-config3/src/main/java/com/addthis/metrics3/reporter/config/PrometheusReporter.java
rm reporter-config3/src/main/java/com/addthis/metrics3/reporter/config/PrometheusReporterConfig.java
rm reporter-config3/src/test/java/com/addthis/metrics3/reporter/config/StatsDReporterConfigTest.java

# remove files using optional dependencies for SCL package
%{?scl:rm reporter-config3/src/main/java/com/addthis/metrics3/reporter/config/ConsoleReporterConfig.java
rm reporter-config3/src/main/java/com/addthis/metrics3/reporter/config/GangliaReporterConfig.java
rm reporter-config3/src/main/java/com/addthis/metrics3/reporter/config/GraphiteReporterConfig.java}

# removeOptionalDeps patch
%patch0 -p1

# removeSCLOptionalDeps patch
%{?scl:%patch1 -p1}

# change maven-compiler-plugin source so that it supports diamond operators
%pom_add_plugin :maven-compiler-plugin . "<configuration>
<source>7</source>
<target>1.7</target>
</configuration>"
%{?scl:EOF}

%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_build -- -Dproject.build.sourceEncoding=UTF-8
%{?scl:EOF}

%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_install
%{?scl:EOF}

%files -f .mfiles
%doc README.mdown
%license LICENSE NOTICE

%files javadoc -f .mfiles-javadoc
%license LICENSE NOTICE

%changelog
* Wed Nov 02 2016 Tomas Repik <trepik@redhat.com> - 3.0.3-2
- scl conversion

* Wed Sep 14 2016 Tomas Repik <trepik@redhat.com> - 3.0.3-1
- version update

* Tue Aug 23 2016 Tomas Repik <trepik@redhat.com> - 3.0.2-1
- version update
- removed optional depenedencies that are not needed for cassandra

* Wed Mar 23 2016 Tomas Repik <trepik@redhat.com> - 3.0.0-1
- Initial RPM release

