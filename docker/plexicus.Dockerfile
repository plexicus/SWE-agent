FROM ubuntu:jammy

ARG TARGETARCH
ENV PYTHONDONTWRITEBYTECODE=1

# Update repositories and install base tools
RUN apt-get update && \
    apt-get install -y bash gcc git jq wget g++ make curl build-essential unzip cmake && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configure Git
RUN git config --global user.email "sweagent@pnlp.org" && \
    git config --global user.name "sweagent"

# Set environment variables and alias
ENV ROOT='/dev/'
RUN echo "alias ls='ls -F'" >> /root/.bashrc
ENV PS1="> "

# ----------------------------
# Install Miniconda for Python & package managers (pip, conda)
# ----------------------------
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
COPY docker/getconda.sh .
RUN bash getconda.sh ${TARGETARCH} \
    && rm getconda.sh \
    && mkdir /root/.conda \
    && bash miniconda.sh -b \
    && rm -f miniconda.sh
RUN conda --version && conda init bash && conda config --append channels conda-forge

# Create environments for Python 3.11 and 3.12
RUN conda create -y -n python3.11 python=3.11 && \
    conda create -y -n python3.12 python=3.12

# Install additional Python build tools if needed (e.g., pip packages)
COPY docker/requirements.txt /root/requirements.txt
RUN pip install -r /root/requirements.txt

# ----------------------------
# Install Node.js (JavaScript & TypeScript) and package managers (npm, yarn)
# ----------------------------
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get update && \
    apt-get install -y nodejs && \
    node --version && \
    npm --version && \
    npm install -g typescript yarn

# ----------------------------
# Install Java (OpenJDK 21 LTS) and build tools (Maven, Gradle)
# ----------------------------
RUN apt-get update && \
    apt-get install -y openjdk-21-jdk && \
    java -version && \
    apt-get install -y maven gradle

# ----------------------------
# Install .NET (C# 12 / .NET 8) and associated CLI tools
# ----------------------------
RUN wget https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && rm packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y dotnet-sdk-8.0 && \
    dotnet --version

# ----------------------------
# Install C/C++ compilers and build tools (cmake, make)
# ----------------------------
# build-essential, gcc and g++ already installed above.
RUN gcc --version && g++ --version && cmake --version

# ----------------------------
# Install PHP (PHP 8.2) and Composer (dependency manager)
# ----------------------------
RUN apt-get update && \
    apt-get install -y php8.2 php8.2-cli php8.2-common php8.2-mbstring php8.2-xml && \
    php --version && \
    curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer && \
    composer --version

# ----------------------------
# Install Go (Go 1.22) and related tools
# ----------------------------
RUN wget https://golang.org/dl/go1.22.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.22.linux-amd64.tar.gz && \
    rm go1.22.linux-amd64.tar.gz && \
    echo "export PATH=\$PATH:/usr/local/go/bin" >> /etc/profile && \
    /bin/bash -c "source /etc/profile" && \
    go version

# ----------------------------
# Install Kotlin (Kotlin 1.9) and optionally Gradle for Kotlin projects
# ----------------------------
RUN wget https://github.com/JetBrains/kotlin/releases/download/v1.9.0/kotlin-compiler-1.9.0.zip && \
    unzip kotlin-compiler-1.9.0.zip -d /opt/kotlin && \
    rm kotlin-compiler-1.9.0.zip && \
    ln -s /opt/kotlin/bin/kotlinc /usr/local/bin/kotlinc && \
    kotlinc -version

# ----------------------------
# Install Rust (Rust 1.75 / 1.76) and Cargo (package manager)
# ----------------------------
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    /root/.cargo/bin/rustc --version && \
    /root/.cargo/bin/cargo --version

# ----------------------------
# Install Swift (Swift 5.9) and Swift Package Manager
# Note: Swift installation on Ubuntu might require additional dependencies.
# ----------------------------
RUN wget https://download.swift.org/swift-5.9-release/ubuntu2004/swift-5.9-RELEASE/swift-5.9-RELEASE-ubuntu20.04.tar.gz && \
    tar -xzf swift-5.9-RELEASE-ubuntu20.04.tar.gz -C /opt && \
    rm swift-5.9-RELEASE-ubuntu20.04.tar.gz && \
    ln -s /opt/swift-5.9-RELEASE-ubuntu20.04/usr/bin/swift /usr/local/bin/swift && \
    swift --version

WORKDIR /
CMD ["/bin/bash"]
